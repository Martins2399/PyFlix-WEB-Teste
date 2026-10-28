"""Copy PyFlix SQLite users and films to the PostgreSQL DATABASE_URL."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from sqlalchemy import URL, create_engine, insert, inspect, select, text
from werkzeug.security import generate_password_hash

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database import DEFAULT_SQLITE_PATH, filmes, make_engine, metadata, usuarios


def is_password_hash(value: str) -> bool:
    return value.startswith(("scrypt:", "pbkdf2:"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migra contas e filmes do SQLite para o PostgreSQL configurado em DATABASE_URL."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Grava os dados no PostgreSQL. Sem esta opção, apenas exibe a contagem de origem.",
    )
    args = parser.parse_args()

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        parser.error("Defina DATABASE_URL com a conexão do banco PostgreSQL de destino.")

    sqlite_path = Path(os.getenv("PYFLIX_SQLITE_PATH", str(DEFAULT_SQLITE_PATH)))
    if not sqlite_path.is_file():
        parser.error(f"Banco SQLite de origem não encontrado: {sqlite_path}")

    source_engine = create_engine(URL.create("sqlite", database=str(sqlite_path)))
    destination_engine = make_engine(database_url)
    if destination_engine.dialect.name != "postgresql":
        parser.error("O destino em DATABASE_URL precisa ser PostgreSQL.")

    source_tables = set(inspect(source_engine).get_table_names())
    if "usuarios" not in source_tables:
        parser.error(f"A tabela usuarios não existe no SQLite de origem: {sqlite_path}")

    with source_engine.connect() as source:
        user_rows = source.execute(select(usuarios)).mappings().all()
        film_rows = (
            source.execute(select(filmes)).mappings().all()
            if "filmes" in source_tables
            else []
        )

    print(f"Origem SQLite: {len(user_rows)} contas e {len(film_rows)} filmes.")
    if not args.apply:
        print("Prévia somente leitura. Use --apply para copiar os registros.")
        return 0

    metadata.create_all(destination_engine)
    copied_users = 0
    copied_films = 0

    with destination_engine.begin() as destination:
        existing_emails = set(destination.execute(select(usuarios.c.email)).scalars())
        existing_user_ids = set(destination.execute(select(usuarios.c.id)).scalars())
        existing_film_titles = set(destination.execute(select(filmes.c.titulo)).scalars())
        existing_film_ids = set(destination.execute(select(filmes.c.id)).scalars())

        for row in user_rows:
            if row["email"] in existing_emails:
                continue
            values = dict(row)
            if values["id"] in existing_user_ids:
                values.pop("id")
            if not is_password_hash(values["senha"]):
                values["senha"] = generate_password_hash(values["senha"])
            result = destination.execute(insert(usuarios).values(**values))
            inserted_id = result.inserted_primary_key[0]
            existing_user_ids.add(inserted_id)
            existing_emails.add(row["email"])
            copied_users += 1

        for row in film_rows:
            if row["titulo"] in existing_film_titles:
                continue
            values = dict(row)
            if values["id"] in existing_film_ids:
                values.pop("id")
            result = destination.execute(insert(filmes).values(**values))
            existing_film_ids.add(result.inserted_primary_key[0])
            existing_film_titles.add(row["titulo"])
            copied_films += 1

        for table_name in ("usuarios", "filmes"):
            max_id = destination.execute(text(f'SELECT MAX(id) FROM "{table_name}"')).scalar_one()
            if max_id is not None:
                destination.execute(
                    text(
                        "SELECT setval(pg_get_serial_sequence(:table_name, 'id'), :max_id, true)"
                    ),
                    {"table_name": table_name, "max_id": max_id},
                )

    print(f"Migração concluída: {copied_users} contas e {copied_films} filmes copiados.")
    print("Registros que já existiam no destino foram mantidos sem alteração.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

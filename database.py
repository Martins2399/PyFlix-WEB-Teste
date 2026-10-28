"""Database setup and seed data for the PyFlix web app."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    URL,
    create_engine,
    insert,
    make_url,
    select,
)
from sqlalchemy.engine import Engine


ROOT_DIR = Path(__file__).resolve().parent
STATIC_DIR = ROOT_DIR / "static"
DEFAULT_SQLITE_PATH = ROOT_DIR / "PyFlix - WEB" / "usuarios.db"
LOGGER = logging.getLogger(__name__)

metadata = MetaData()

usuarios = Table(
    "usuarios",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("nome", String(100), nullable=False),
    Column("email", String(254), nullable=False, unique=True, index=True),
    Column("senha", String(255), nullable=False),
)

filmes = Table(
    "filmes",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("titulo", String(180), nullable=False),
    Column("descricao", Text, nullable=False),
    Column("categoria", String(80), nullable=False, index=True),
    Column("imagem", String(255), nullable=False),
    Column("video", String(255), nullable=False),
    Column("ordem", Integer, nullable=False, default=0),
    Column("destaque", Boolean, nullable=False, default=False),
    Column("ativo", Boolean, nullable=False, default=True, index=True),
)

FILMES_DEMO = [
    {
        "titulo": "Exterminador do Futuro 7",
        "descricao": "O futuro é incerto, mas a luta pela sobrevivência é certa.",
        "categoria": "Ação",
        "imagem": "images/exterminador_7.webp",
        "video": "videos/exterminador_7.mp4",
        "ordem": 1,
        "destaque": True,
        "ativo": True,
    },
    {
        "titulo": "A 5ª Onda",
        "descricao": "Quando a humanidade enfrenta uma ameaça inesperada, a esperança transforma-se em luta.",
        "categoria": "Ação",
        "imagem": "images/a-5-onda.webp",
        "video": "videos/a-5-onda.mp4",
        "ordem": 2,
        "destaque": False,
        "ativo": True,
    },
    {
        "titulo": "Minecraft: O Filme",
        "descricao": "Uma aventura emocionante no mundo de blocos e criatividade.",
        "categoria": "Comédia",
        "imagem": "images/minecraft-o-filme.webp",
        "video": "videos/minecraft-o-filme.mp4",
        "ordem": 3,
        "destaque": False,
        "ativo": True,
    },
    {
        "titulo": "Terror no Rio",
        "descricao": "Uma história de terror que se desenrola nas águas turbulentas de um rio misterioso.",
        "categoria": "Terror",
        "imagem": "images/terror-rio.webp",
        "video": "videos/terror-rio.mp4",
        "ordem": 4,
        "destaque": False,
        "ativo": True,
    },
    {
        "titulo": "Maldição da Múmia",
        "descricao": "Uma antiga maldição desperta quando um arqueólogo desenterra um sarcófago.",
        "categoria": "Terror",
        "imagem": "images/maldicao-da-mumia.webp",
        "video": "videos/maldicao-da-mumia.mp4",
        "ordem": 5,
        "destaque": False,
        "ativo": True,
    },
    {
        "titulo": "Sim Senhor",
        "descricao": "Uma história de amor que transcende o tempo e as circunstâncias.",
        "categoria": "Romance",
        "imagem": "images/sim-senhor.webp",
        "video": "videos/sim-senhor.mp4",
        "ordem": 6,
        "destaque": False,
        "ativo": True,
    },
    {
        "titulo": "Animais Fantásticos",
        "descricao": "Uma aventura de criaturas mágicas e desafios intensos.",
        "categoria": "Fantasia",
        "imagem": "images/animais-fantasticos.webp",
        "video": "videos/animais-fantasticos.mp4",
        "ordem": 7,
        "destaque": False,
        "ativo": True,
    },
]


def normalize_database_url(database_url: str) -> str:
    """Normalize hosted PostgreSQL URLs for the psycopg 3 SQLAlchemy driver."""
    if database_url.startswith("postgres://"):
        return "postgresql+psycopg://" + database_url.removeprefix("postgres://")
    if database_url.startswith("postgresql://"):
        return "postgresql+psycopg://" + database_url.removeprefix("postgresql://")
    return database_url


def make_engine(database_url: str | None = None) -> Engine:
    """Create a SQLite engine locally or a PostgreSQL engine when configured."""
    database_url = database_url or os.getenv("DATABASE_URL")
    if not database_url:
        sqlite_path = Path(os.getenv("PYFLIX_SQLITE_PATH", str(DEFAULT_SQLITE_PATH)))
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        database_url = URL.create("sqlite", database=str(sqlite_path))
    else:
        database_url = normalize_database_url(database_url)

    parsed_url = make_url(database_url)
    connect_args = {"check_same_thread": False} if parsed_url.get_backend_name() == "sqlite" else {}
    return create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)


def is_safe_media_file(relative_path: str, expected_folder: str) -> bool:
    """Ensure a database media reference stays inside the app's static assets."""
    candidate = Path(relative_path)
    if candidate.is_absolute() or ".." in candidate.parts or not candidate.parts:
        return False
    if candidate.parts[0] != expected_folder:
        return False

    static_root = STATIC_DIR.resolve()
    file_path = (static_root / candidate).resolve()
    return file_path.is_relative_to(static_root) and file_path.is_file()


def initialize_database(engine: Engine, *, seed_catalog: bool = True) -> None:
    """Create any missing tables and add demo films only to an empty catalog."""
    metadata.create_all(engine)
    if not seed_catalog:
        return

    with engine.begin() as connection:
        has_films = connection.execute(select(filmes.c.id).limit(1)).first()
        if has_films:
            return

        available_films = [
            film
            for film in FILMES_DEMO
            if is_safe_media_file(film["imagem"], "images")
            and is_safe_media_file(film["video"], "videos")
        ]
        if available_films:
            connection.execute(insert(filmes), available_films)
        else:
            LOGGER.warning("Catálogo vazio: nenhum arquivo de demonstração foi encontrado.")

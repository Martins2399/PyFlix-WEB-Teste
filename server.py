"""Flask API and page server for PyFlix."""

from __future__ import annotations

import hmac
import logging
import os
import re
from datetime import timedelta
from urllib.parse import urlsplit

from flask import Flask, abort, jsonify, request, send_from_directory, session
from sqlalchemy import desc, insert, select, update
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from database import ROOT_DIR, filmes, initialize_database, is_safe_media_file, make_engine, usuarios


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
HASH_PREFIXES = ("scrypt:", "pbkdf2:")
LOGGER = logging.getLogger(__name__)
_DUMMY_PASSWORD_HASH = generate_password_hash("not-a-real-pyflix-password")


def _public_user(row: dict) -> dict:
    return {"id": int(row["id"]), "nome": row["nome"], "email": row["email"]}


def _password_is_hash(value: str) -> bool:
    return value.startswith(HASH_PREFIXES)


def _password_matches(stored_password: str, submitted_password: str) -> tuple[bool, bool]:
    """Return (matched, legacy_plaintext) while upgrading old SQLite accounts."""
    if _password_is_hash(stored_password):
        try:
            return check_password_hash(stored_password, submitted_password), False
        except (TypeError, ValueError):
            return False, False
    return hmac.compare_digest(stored_password, submitted_password), True


def create_app(
    config: dict | None = None,
    *,
    database_url: str | None = None,
) -> Flask:
    app = Flask(
        __name__,
        static_folder=str(ROOT_DIR / "static"),
        static_url_path="/static",
    )

    supplied_config = config or {}
    secret_key = supplied_config.get("SECRET_KEY") or os.getenv("SESSION_SECRET")
    if not secret_key:
        raise RuntimeError("Configure o segredo SESSION_SECRET antes de iniciar o servidor.")
    app_environment = str(
        supplied_config.get("APP_ENV") or os.getenv("APP_ENV", "development")
    ).lower()

    app.config.from_mapping(
        SECRET_KEY=secret_key,
        APP_ENV=app_environment,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=app_environment == "production",
        PERMANENT_SESSION_LIFETIME=timedelta(days=14),
        MAX_CONTENT_LENGTH=32 * 1024,
    )
    app.config.update(supplied_config)

    resolved_database_url = database_url or app.config.get("DATABASE_URL") or os.getenv("DATABASE_URL")
    if app.config["APP_ENV"].lower() == "production" and not resolved_database_url:
        raise RuntimeError("Configure DATABASE_URL com um banco persistente antes de iniciar em produção.")

    engine = make_engine(resolved_database_url)
    if app.config["APP_ENV"].lower() == "production" and engine.dialect.name != "postgresql":
        engine.dispose()
        raise RuntimeError("Em produção, use um banco PostgreSQL persistente em DATABASE_URL.")
    initialize_database(engine)
    app.extensions["pyflix_engine"] = engine

    def get_engine():
        return app.extensions["pyflix_engine"]

    def find_user_by_id(user_id: int | str):
        with get_engine().connect() as connection:
            return connection.execute(
                select(usuarios.c.id, usuarios.c.nome, usuarios.c.email)
                .where(usuarios.c.id == user_id)
            ).mappings().first()

    def current_user():
        user_id = session.get("user_id")
        if user_id is None:
            return None
        row = find_user_by_id(user_id)
        if row is None:
            session.clear()
        return row

    def start_session(row: dict) -> dict:
        session.clear()
        session.permanent = True
        session["user_id"] = int(row["id"])
        return _public_user(row)

    @app.before_request
    def reject_cross_origin_auth_posts():
        if request.path not in {"/api/registar", "/api/login", "/api/logout"}:
            return None
        if request.method != "POST":
            return None

        origin = request.headers.get("Origin")
        if not origin:
            return None
        origin_host = urlsplit(origin).netloc.lower()
        if origin_host and origin_host != request.host.lower():
            return jsonify(mensagem="Origem da solicitação não autorizada."), 403
        return None

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response

    @app.get("/")
    def index():
        return send_from_directory(ROOT_DIR, "index.html")

    @app.get("/health")
    def health():
        try:
            with get_engine().connect() as connection:
                connection.exec_driver_sql("SELECT 1")
            return jsonify(status="ok")
        except Exception:
            LOGGER.exception("Health check do banco falhou.")
            return jsonify(status="error"), 503

    @app.get("/api/me")
    def get_session():
        user = current_user()
        return jsonify(autenticado=user is not None, utilizador=_public_user(user) if user else None)

    @app.post("/api/registar")
    def register():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(mensagem="Envie os dados do cadastro em JSON."), 400

        nome = str(payload.get("nome", "")).strip()
        email = str(payload.get("email", "")).strip().lower()
        senha = payload.get("senha")
        if not isinstance(senha, str):
            senha = ""

        if not 2 <= len(nome) <= 100:
            return jsonify(mensagem="Informe um nome entre 2 e 100 caracteres."), 400
        if len(email) > 254 or not EMAIL_PATTERN.fullmatch(email):
            return jsonify(mensagem="Informe um e-mail válido."), 400
        if not 8 <= len(senha) <= 128:
            return jsonify(mensagem="A senha deve ter entre 8 e 128 caracteres."), 400

        try:
            with get_engine().begin() as connection:
                result = connection.execute(
                    insert(usuarios).values(
                        nome=nome,
                        email=email,
                        senha=generate_password_hash(senha),
                    )
                )
                row = connection.execute(
                    select(usuarios.c.id, usuarios.c.nome, usuarios.c.email)
                    .where(usuarios.c.id == result.inserted_primary_key[0])
                ).mappings().one()
        except IntegrityError:
            return jsonify(mensagem="Já existe uma conta com esse e-mail."), 409

        public_user = start_session(row)
        return jsonify(mensagem="Conta criada com sucesso.", utilizador=public_user), 201

    @app.post("/api/login")
    def login():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(mensagem="E-mail ou senha incorretos."), 401

        email = str(payload.get("email", "")).strip().lower()
        senha = payload.get("senha")
        if not isinstance(senha, str) or len(senha) > 128 or not email:
            check_password_hash(_DUMMY_PASSWORD_HASH, "invalid")
            return jsonify(mensagem="E-mail ou senha incorretos."), 401

        with get_engine().connect() as connection:
            row = connection.execute(
                select(usuarios)
                .where(usuarios.c.email == email)
            ).mappings().first()

        if row is None:
            check_password_hash(_DUMMY_PASSWORD_HASH, senha)
            return jsonify(mensagem="E-mail ou senha incorretos."), 401

        matched, legacy_plaintext = _password_matches(row["senha"], senha)
        if not matched:
            return jsonify(mensagem="E-mail ou senha incorretos."), 401

        if legacy_plaintext:
            with get_engine().begin() as connection:
                connection.execute(
                    update(usuarios)
                    .where(usuarios.c.id == row["id"])
                    .values(senha=generate_password_hash(senha))
                )

        public_user = start_session(row)
        return jsonify(mensagem="Login realizado com sucesso.", utilizador=public_user)

    @app.post("/api/logout")
    def logout():
        session.clear()
        return jsonify(mensagem="Sessão encerrada.")

    @app.get("/api/filmes")
    def get_films():
        with get_engine().connect() as connection:
            rows = connection.execute(
                select(filmes)
                .where(filmes.c.ativo.is_(True))
                .order_by(desc(filmes.c.destaque), filmes.c.ordem, filmes.c.id)
            ).mappings().all()

        catalog = []
        for row in rows:
            if not is_safe_media_file(row["imagem"], "images") or not is_safe_media_file(row["video"], "videos"):
                LOGGER.warning("Filme %s ignorado por referência de mídia inválida.", row["id"])
                continue
            catalog.append(
                {
                    "id": int(row["id"]),
                    "titulo": row["titulo"],
                    "descricao": row["descricao"],
                    "categoria": row["categoria"],
                    "imagem": row["imagem"],
                    "video": row["video"],
                    "destaque": bool(row["destaque"]),
                }
            )
        return jsonify(filmes=catalog, total=len(catalog))

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)

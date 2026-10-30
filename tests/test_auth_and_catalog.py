from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("SESSION_SECRET", "test-only-session-secret")

_IMPORT_TIME_DATABASE = tempfile.TemporaryDirectory()
_PREVIOUS_DATABASE_URL = os.environ.get("DATABASE_URL")
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_IMPORT_TIME_DATABASE.name) / 'module-import.db'}"

from sqlalchemy import delete, func, insert, select
from werkzeug.security import check_password_hash

from database import FILMES_DEMO, filmes, initialize_database, usuarios
from server import app as _default_app, create_app

if _PREVIOUS_DATABASE_URL is None:
    os.environ.pop("DATABASE_URL", None)
else:
    os.environ["DATABASE_URL"] = _PREVIOUS_DATABASE_URL


class PyFlixAuthAndCatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_dir.name) / "test.db"
        self.app = create_app(
            {"TESTING": True, "SECRET_KEY": "unit-test-only"},
            database_url=f"sqlite:///{database_path}",
        )
        self.client = self.app.test_client()
        self.engine = self.app.extensions["pyflix_engine"]

    def tearDown(self):
        self.engine.dispose()
        self.temp_dir.cleanup()

    def register(self, *, nome="Ana Silva", email="ana@example.com", senha="senha-segura-123"):
        return self.client.post(
            "/api/registar",
            json={"nome": nome, "email": email, "senha": senha},
        )

    def test_register_persists_hashed_password_and_creates_session(self):
        response = self.register()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["utilizador"]["email"], "ana@example.com")
        self.assertTrue(response.headers.get("Set-Cookie"))

        with self.engine.connect() as connection:
            stored_password = connection.execute(
                select(usuarios.c.senha).where(usuarios.c.email == "ana@example.com")
            ).scalar_one()
        self.assertNotEqual(stored_password, "senha-segura-123")
        self.assertTrue(check_password_hash(stored_password, "senha-segura-123"))

        session_response = self.client.get("/api/me")
        self.assertTrue(session_response.json["autenticado"])
        self.assertEqual(session_response.json["utilizador"]["nome"], "Ana Silva")

    def test_register_validates_fields_and_rejects_duplicate_email_case_insensitively(self):
        short_password = self.register(senha="123")
        self.assertEqual(short_password.status_code, 400)

        first = self.register(email="Ana@Example.com")
        duplicate = self.register(email="ana@example.com")
        self.assertEqual(first.status_code, 201)
        self.assertEqual(duplicate.status_code, 409)

    def test_login_rejects_wrong_password_and_accepts_correct_password(self):
        self.register()
        wrong_password = self.client.post(
            "/api/login",
            json={"email": "ana@example.com", "senha": "errada"},
        )
        self.assertEqual(wrong_password.status_code, 401)

        correct_password = self.client.post(
            "/api/login",
            json={"email": "ANA@example.com", "senha": "senha-segura-123"},
        )
        self.assertEqual(correct_password.status_code, 200)
        self.assertTrue(self.client.get("/api/me").json["autenticado"])

    def test_legacy_plaintext_password_is_upgraded_on_successful_login(self):
        with self.engine.begin() as connection:
            connection.execute(
                insert(usuarios).values(nome="Conta antiga", email="antiga@example.com", senha="senha-antiga")
            )

        response = self.client.post(
            "/api/login",
            json={"email": "antiga@example.com", "senha": "senha-antiga"},
        )
        self.assertEqual(response.status_code, 200)

        with self.engine.connect() as connection:
            stored_password = connection.execute(
                select(usuarios.c.senha).where(usuarios.c.email == "antiga@example.com")
            ).scalar_one()
        self.assertTrue(check_password_hash(stored_password, "senha-antiga"))

    def test_logout_clears_session(self):
        self.register()
        response = self.client.post("/api/logout")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.client.get("/api/me").json["autenticado"])

    def test_catalog_is_read_from_database_and_media_exists(self):
        response = self.client.get("/api/filmes")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["total"], len(FILMES_DEMO))
        self.assertEqual(response.json["filmes"][0]["titulo"], "Exterminador do Futuro 7")

        root = Path(__file__).resolve().parents[1]
        for film in response.json["filmes"]:
            self.assertTrue((root / "static" / film["imagem"]).is_file())
            if film["video_tipo"] == "local":
                self.assertTrue((root / "static" / film["video_url"]).is_file())
            else:
                self.assertRegex(
                    film["video_url"],
                    r"^https://www\.youtube-nocookie\.com/embed/[A-Za-z0-9_-]{11}\?rel=0$",
                )

        documentaries = [
            film for film in response.json["filmes"]
            if film["categoria"] == "Documentário"
        ]
        self.assertEqual(len(documentaries), 3)

    def test_catalog_initialization_appends_missing_demo_movies_without_duplicates(self):
        new_titles = [film["titulo"] for film in FILMES_DEMO[7:]]
        with self.engine.begin() as connection:
            connection.execute(delete(filmes).where(filmes.c.titulo.in_(new_titles)))

        initialize_database(self.engine)
        initialize_database(self.engine)

        with self.engine.connect() as connection:
            count = connection.execute(select(func.count()).select_from(filmes)).scalar_one()
            mad_max_count = connection.execute(
                select(func.count()).select_from(filmes).where(filmes.c.titulo == "Mad Max: Estrada da Fúria")
            ).scalar_one()

        self.assertEqual(count, len(FILMES_DEMO))
        self.assertEqual(mad_max_count, 1)

    def test_page_health_and_same_origin_registration(self):
        page = self.client.get("/")
        health = self.client.get("/health")
        registration = self.client.post(
            "/api/registar",
            json={"nome": "Ana Silva", "email": "ana@example.com", "senha": "senha-segura-123"},
            headers={"Origin": "http://localhost"},
        )

        self.assertEqual(page.status_code, 200)
        self.assertIn(b'<html lang="pt-BR">', page.data)
        self.assertEqual(health.status_code, 200)
        self.assertEqual(registration.status_code, 201)
        page.close()

    def test_authentication_rejects_cross_origin_posts(self):
        response = self.client.post(
            "/api/login",
            json={"email": "nobody@example.invalid", "senha": "senha-segura-123"},
            headers={"Origin": "https://attacker.example"},
        )
        self.assertEqual(response.status_code, 403)

    def test_production_rejects_sqlite(self):
        with self.assertRaisesRegex(RuntimeError, "PostgreSQL persistente"):
            create_app(
                {
                    "TESTING": True,
                    "SECRET_KEY": "unit-test-only",
                    "APP_ENV": "production",
                },
                database_url=f"sqlite:///{Path(self.temp_dir.name) / 'production.db'}",
            )


def tearDownModule():
    _default_app.extensions["pyflix_engine"].dispose()
    _IMPORT_TIME_DATABASE.cleanup()


if __name__ == "__main__":
    unittest.main()

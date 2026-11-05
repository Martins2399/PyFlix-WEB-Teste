"""Database setup and seed data for the PyFlix web app."""

from __future__ import annotations

import logging
import os
import re
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
        "destaque": True,
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
        "destaque": True,
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
    {
        "titulo": "Mad Max: Estrada da Fúria",
        "descricao": "Em uma estrada devastada, Max e Furiosa desafiam uma perseguição implacável em busca de liberdade.",
        "categoria": "Ação",
        "imagem": "images/mad-max-estrada-furia.jpg",
        "video": "youtube:hEJnMQG9ev8",
        "ordem": 8,
        "destaque": True,
        "ativo": True,
    },
    {
        "titulo": "John Wick: Um Novo Dia para Matar",
        "descricao": "Um assassino lendário é atraído de volta ao submundo e enfrenta uma perigosa rede internacional.",
        "categoria": "Ação",
        "imagem": "images/john-wick-2.jpg",
        "video": "youtube:ChpLV9AMqm4",
        "ordem": 9,
        "destaque": False,
        "ativo": True,
    },
    {
        "titulo": "Um Lugar Silencioso",
        "descricao": "Uma família luta para sobreviver em um mundo onde o menor ruído pode ser fatal.",
        "categoria": "Terror",
        "imagem": "images/um-lugar-silencioso.jpg",
        "video": "youtube:WR7cc5t7tv8",
        "ordem": 10,
        "destaque": True,
        "ativo": True,
    },
    {
        "titulo": "Sorria",
        "descricao": "Depois de presenciar um acontecimento perturbador, uma médica passa a enfrentar experiências cada vez mais assustadoras.",
        "categoria": "Terror",
        "imagem": "images/sorria.jpg",
        "video": "youtube:SjnjegNYjs0",
        "ordem": 11,
        "destaque": False,
        "ativo": True,
    },
    {
        "titulo": "Barbie",
        "descricao": "Barbie deixa a Barbielândia e embarca em uma jornada divertida para descobrir seu lugar no mundo.",
        "categoria": "Comédia",
        "imagem": "images/barbie.jpg",
        "video": "youtube:pBk4NYhWNMM",
        "ordem": 12,
        "destaque": False,
        "ativo": True,
    },
    {
        "titulo": "La La Land: Cantando Estações",
        "descricao": "Uma atriz e um pianista perseguem seus sonhos enquanto descobrem um amor que desafia o tempo.",
        "categoria": "Romance",
        "imagem": "images/la-la-land.jpg",
        "video": "youtube:0pdqf4P9MB8",
        "ordem": 13,
        "destaque": False,
        "ativo": True,
    },
    {
        "titulo": "Wonka",
        "descricao": "Antes de se tornar o maior chocolatier do mundo, um jovem inventor transforma a cidade com imaginação.",
        "categoria": "Fantasia",
        "imagem": "images/wonka.jpg",
        "video": "youtube:oACMU-w1RXw",
        "ordem": 14,
        "destaque": False,
        "ativo": True,
    },
    {
        "titulo": "Free Solo",
        "descricao": "O escalador Alex Honnold se prepara para realizar uma subida histórica sem cordas.",
        "categoria": "Documentário",
        "imagem": "images/free-solo.jpg",
        "video": "youtube:urRVZ4SW7WU",
        "ordem": 15,
        "destaque": True,
        "ativo": True,
    },
    {
        "titulo": "Meu Professor Polvo",
        "descricao": "Um cineasta cria uma amizade improvável com um polvo em uma floresta de algas sul-africana.",
        "categoria": "Documentário",
        "imagem": "images/meu-professor-polvo.jpg",
        "video": "youtube:3s0LTDhqe5A",
        "ordem": 16,
        "destaque": False,
        "ativo": True,
    },
    {
        "titulo": "A Vida no Nosso Planeta",
        "descricao": "Uma viagem pela história da vida na Terra, das criaturas pré-históricas aos ecossistemas atuais.",
        "categoria": "Documentário",
        "imagem": "images/nosso-planeta.jpg",
        "video": "youtube:xy1v0pzMP4g",
        "ordem": 17,
        "destaque": False,
        "ativo": True,
    },
]

YOUTUBE_VIDEO_REFERENCE = re.compile(r"^youtube:([A-Za-z0-9_-]{11})$")


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


def video_reference_type(reference: str) -> str | None:
    """Accept local trailers or an 11-character YouTube video ID marker."""
    if not isinstance(reference, str):
        return None
    if YOUTUBE_VIDEO_REFERENCE.fullmatch(reference):
        return "youtube"
    if is_safe_media_file(reference, "videos"):
        return "local"
    return None


def initialize_database(engine: Engine, *, seed_catalog: bool = True) -> None:
    """Create tables and append missing demo films without overwriting existing rows."""
    metadata.create_all(engine)
    if not seed_catalog:
        return

    with engine.begin() as connection:
        existing_titles = set(connection.execute(select(filmes.c.titulo)).scalars())

        available_films = [
            film
            for film in FILMES_DEMO
            if film["titulo"] not in existing_titles
            and is_safe_media_file(film["imagem"], "images")
            and video_reference_type(film["video"]) is not None
        ]
        if available_films5 := available_films:
            connection.execute(insert(filmes), available_films5)
            LOGGER.info("%s novos filmes de demonstração adicionados ao catálogo.", len(available_films5))
        else:
            LOGGER.debug("Nenhum novo filme de demonstração foi adicionado.")
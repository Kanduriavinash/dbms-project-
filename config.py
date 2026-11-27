import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration. Secrets are supplied through environment variables."""

    # Use SQLite for a safe local default. Set DATABASE_URL to use PostgreSQL.
    DATABASE_URL = os.environ.get("DATABASE_URL") or "sqlite:///rims.db"

    # Render/Heroku-style postgres:// URLs are normalized for SQLAlchemy.
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    if DATABASE_URL.startswith("postgresql://"):
        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace(
            "postgresql://", "postgresql+psycopg2://", 1
        )
    elif DATABASE_URL.startswith("postgresql+psycopg2://"):
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL

    # A random per-process fallback is suitable only for local development.
    # Deployments should always set a stable, high-entropy SECRET_KEY.
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(32)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

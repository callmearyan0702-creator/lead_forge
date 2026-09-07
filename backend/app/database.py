"""
SQLAlchemy engine + session management.

Kept deliberately small: one engine, one sessionmaker, one dependency
(`get_db`) that FastAPI routes use. Swapping Postgres for another
SQLAlchemy-supported database later is a one-line change to DATABASE_URL.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import get_settings

settings = get_settings()

# `connect_args` only matters for SQLite (used in local/dev/testing);
# Postgres ignores it via the branch below.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

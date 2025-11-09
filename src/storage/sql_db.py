from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config.settings import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

SQLITE_BASE = declarative_base()


def create_tables(engine: Engine):
    """Create all tables in the database."""
    SQLITE_BASE.metadata.create_all(engine)
    logger.info("Database tables created")


def get_engine(db_path: str = settings.sqlite_path):
    """
    Get SQLAlchemy engine.

    Args:
        db_path: Path to SQLite database

    Returns:
        SQLAlchemy engine
    """
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    logger.info(f"Database engine created: {db_path}")
    return engine


def get_session_factory(engine):
    """
    Get SQLAlchemy session factory.

    Args:
        engine: SQLAlchemy engine

    Returns:
        Session factory
    """
    return sessionmaker(bind=engine)

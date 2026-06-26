import logging

from sqlalchemy.engine import make_url

from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.services.bootstrap import seed_defaults

logger = logging.getLogger(__name__)


def create_tables_if_needed() -> None:
    if settings.should_create_tables_on_startup:
        # SQLAlchemy create_all is intentionally non-destructive: it creates
        # missing tables only and never drops existing user data.
        Base.metadata.create_all(bind=engine)


def validate_persistence_configuration() -> None:
    if not settings.is_sqlite:
        return
    url = make_url(settings.DATABASE_URL)
    database_path = url.database or ""
    if database_path == ":memory:":
        logger.warning("SQLite is running in memory. This is not durable and must never be used for production data.")
        return
    if settings.ENVIRONMENT.lower() in {"production", "prod"} and not database_path.startswith("/var/data/"):
        logger.warning(
            "SQLite production database is not under /var/data. On Render, use a Persistent Disk and "
            "DATABASE_URL=sqlite:////var/data/mawahib.db, or use PostgreSQL to avoid data loss."
        )


def initialize_database() -> None:
    validate_persistence_configuration()
    create_tables_if_needed()
    db = SessionLocal()
    try:
        seed_defaults(db)
    finally:
        db.close()


if __name__ == "__main__":
    initialize_database()

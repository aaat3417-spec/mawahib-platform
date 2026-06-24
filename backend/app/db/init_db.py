from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.services.bootstrap import seed_defaults


def create_tables_if_needed() -> None:
    if settings.should_create_tables_on_startup:
        Base.metadata.create_all(bind=engine)


def initialize_database() -> None:
    create_tables_if_needed()
    db = SessionLocal()
    try:
        seed_defaults(db)
    finally:
        db.close()


if __name__ == "__main__":
    initialize_database()

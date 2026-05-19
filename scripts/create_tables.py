"""
Utility script to create all ORM-mapped tables in the database.
Run once if the tables don't already exist:
    python scripts/create_tables.py
"""
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.auth_session_model import AuthSessionModel  # noqa: F401
from app.infrastructure.db.models.user_model import UserModel  # noqa: F401
from app.infrastructure.db.session import engine

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("Tables created (or already exist).")

# database.py

from collections.abc import Generator
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./suot.db")

# Connection between manager between the app and SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    expire_on_commit=False, 
    autoflush=False, 
    bind=engine
)

class Base(DeclarativeBase):
    pass

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


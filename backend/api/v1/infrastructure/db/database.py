from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Для простоты по умолчанию используем SQLite (файл) для локальной разработки и тестов.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Для простого примера используем обычный (sync) engine + ORM
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
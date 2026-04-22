from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os

if os.getenv("TESTING") == "true":
    DATABASE_URL = "sqlite:///./test_kanban.db"
elif os.getenv("VERCEL"):
    DATABASE_URL = "sqlite:////tmp/kanban.db"
else:
    DATABASE_URL = "sqlite:///./kanban.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

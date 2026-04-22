import pytest
import os

# Set testing mode before any imports
os.environ["TESTING"] = "true"

# This imports must happen AFTER setting TESTING to use in-memory DB
from src.backend.main import app, startup_event
from src.backend.database import engine, Base
from src.backend.models import User, Board, Column as ColumnModel, Card

# Create tables immediately when conftest loads
Base.metadata.create_all(bind=engine)

# Seed initial data
_seed_data_called = False

def seed_database():
    """Seed initial data once"""
    global _seed_data_called
    if _seed_data_called:
        return
    _seed_data_called = True

    from src.backend.database import SessionLocal
    from src.backend.models import User, Board, Column as ColumnModel, Card

    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            user = User(username="user")
            db.add(user)
            db.flush()

            board = Board(user_id=user.id, title="My Project")
            db.add(board)
            db.flush()

            columns = [
                ColumnModel(board_id=board.id, title="To Do", position=0),
                ColumnModel(board_id=board.id, title="In Progress", position=1),
                ColumnModel(board_id=board.id, title="Review", position=2),
                ColumnModel(board_id=board.id, title="Testing", position=3),
                ColumnModel(board_id=board.id, title="Done", position=4),
            ]
            db.add_all(columns)
            db.flush()

            sample_cards = [
                Card(column_id=columns[0].id, title="Design UI mockups", details="Create initial mockups", position=0),
                Card(column_id=columns[0].id, title="Setup database", details="SQLite schema", position=1),
                Card(column_id=columns[1].id, title="Implement login", details="Auth endpoints", position=0),
                Card(column_id=columns[1].id, title="Build Kanban API", details="CRUD endpoints", position=1),
                Card(column_id=columns[2].id, title="Code review", details="Peer review auth", position=0),
                Card(column_id=columns[3].id, title="E2E tests", details="Playwright tests", position=0),
                Card(column_id=columns[4].id, title="Deploy", details="Docker container", position=0),
                Card(column_id=columns[4].id, title="Documentation", details="README and API docs", position=1),
            ]
            db.add_all(sample_cards)
            db.commit()
    finally:
        db.close()

# Seed on import
seed_database()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Ensure database is ready for tests"""
    pass

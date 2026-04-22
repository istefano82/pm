from datetime import datetime
from sqlalchemy import Column as SQLColumn, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = SQLColumn(Integer, primary_key=True, index=True)
    username = SQLColumn(String, unique=True, index=True, nullable=False)
    created_at = SQLColumn(DateTime, default=datetime.utcnow)

    boards = relationship("Board", back_populates="user")


class Board(Base):
    __tablename__ = "boards"

    id = SQLColumn(Integer, primary_key=True, index=True)
    user_id = SQLColumn(Integer, ForeignKey("users.id"), nullable=False)
    title = SQLColumn(String, nullable=False)
    created_at = SQLColumn(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="boards")
    columns = relationship("Column", back_populates="board", cascade="all, delete-orphan")


class Column(Base):
    __tablename__ = "columns"

    id = SQLColumn(Integer, primary_key=True, index=True)
    board_id = SQLColumn(Integer, ForeignKey("boards.id"), nullable=False)
    title = SQLColumn(String, nullable=False)
    position = SQLColumn(Integer, nullable=False)
    created_at = SQLColumn(DateTime, default=datetime.utcnow)

    board = relationship("Board", back_populates="columns")
    cards = relationship("Card", back_populates="column", cascade="all, delete-orphan")


class Card(Base):
    __tablename__ = "cards"

    id = SQLColumn(Integer, primary_key=True, index=True)
    column_id = SQLColumn(Integer, ForeignKey("columns.id"), nullable=False)
    title = SQLColumn(String, nullable=False)
    details = SQLColumn(Text, default="")
    position = SQLColumn(Integer, nullable=False)
    created_at = SQLColumn(DateTime, default=datetime.utcnow)

    column = relationship("Column", back_populates="cards")

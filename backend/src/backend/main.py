from datetime import datetime
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
import secrets

from .database import Base, engine, get_db, SessionLocal
from .models import User, Board, Column as ColumnModel, Card

app = FastAPI(title="Project Management MVP Backend")

# Hardcoded credentials for MVP
VALID_USERNAME = "user"
VALID_PASSWORD = "password"

# Simple in-memory token store (for MVP only - not production)
valid_tokens = set()

# Pydantic schemas
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    message: str


class ColumnUpdate(BaseModel):
    title: str


class CardCreate(BaseModel):
    column_id: int
    title: str
    details: str = ""


class CardUpdate(BaseModel):
    title: str | None = None
    details: str | None = None


class CardMove(BaseModel):
    column_id: int
    position: int


class CardOut(BaseModel):
    id: int
    title: str
    details: str
    position: int

    class Config:
        from_attributes = True


class ColumnOut(BaseModel):
    id: int
    title: str
    position: int
    cards: list[CardOut] = []

    class Config:
        from_attributes = True


class BoardOut(BaseModel):
    id: int
    title: str
    columns: list[ColumnOut] = []

    class Config:
        from_attributes = True


def require_auth(authorization: str = Header(None)) -> str:
    """Validate Bearer token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization[7:]
    if token not in valid_tokens:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return token


@app.on_event("startup")
def startup_event():
    """Create tables and seed initial data"""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if users table is empty
        if db.query(User).count() == 0:
            # Create user
            user = User(username=VALID_USERNAME)
            db.add(user)
            db.flush()

            # Create board
            board = Board(user_id=user.id, title="My Project")
            db.add(board)
            db.flush()

            # Create columns
            columns = [
                ColumnModel(board_id=board.id, title="To Do", position=0),
                ColumnModel(board_id=board.id, title="In Progress", position=1),
                ColumnModel(board_id=board.id, title="Review", position=2),
                ColumnModel(board_id=board.id, title="Testing", position=3),
                ColumnModel(board_id=board.id, title="Done", position=4),
            ]
            db.add_all(columns)
            db.flush()

            # Create sample cards
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


# Auth endpoints
@app.post("/api/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login with hardcoded credentials"""
    if request.username != VALID_USERNAME or request.password != VALID_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = secrets.token_urlsafe(32)
    valid_tokens.add(token)

    return LoginResponse(token=token, message="Login successful")


@app.post("/api/logout")
async def logout(authorization: str = Header(None)):
    """Logout and invalidate token"""
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        valid_tokens.discard(token)

    return {"message": "Logged out successfully"}


@app.get("/api/verify")
async def verify(authorization: str = Header(None)):
    """Verify authentication token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization[7:]
    if token not in valid_tokens:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return {"status": "authenticated"}


@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "Backend is running"}


# Kanban endpoints
@app.get("/api/board", response_model=BoardOut)
async def get_board(token: str = Depends(require_auth), db: Session = Depends(get_db)):
    """Get full board state with columns and cards"""
    user = db.query(User).filter(User.username == VALID_USERNAME).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    board = db.query(Board).filter(Board.user_id == user.id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    # Load columns and cards ordered by position
    columns = db.query(ColumnModel).filter(ColumnModel.board_id == board.id).order_by(ColumnModel.position).all()

    columns_data = []
    for col in columns:
        cards = db.query(Card).filter(Card.column_id == col.id).order_by(Card.position).all()
        columns_data.append(
            ColumnOut(
                id=col.id,
                title=col.title,
                position=col.position,
                cards=[CardOut.model_validate(c) for c in cards]
            )
        )

    return BoardOut(id=board.id, title=board.title, columns=columns_data)


@app.put("/api/columns/{column_id}")
async def rename_column(column_id: int, update: ColumnUpdate, token: str = Depends(require_auth), db: Session = Depends(get_db)):
    """Rename a column"""
    column = db.query(ColumnModel).filter(ColumnModel.id == column_id).first()
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")

    column.title = update.title
    db.commit()

    return {"id": column.id, "title": column.title}


@app.post("/api/cards")
async def create_card(card_data: CardCreate, token: str = Depends(require_auth), db: Session = Depends(get_db)):
    """Create a new card"""
    column = db.query(ColumnModel).filter(ColumnModel.id == card_data.column_id).first()
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")

    # Get max position in column
    max_position = db.query(Card).filter(Card.column_id == card_data.column_id).count()

    card = Card(
        column_id=card_data.column_id,
        title=card_data.title,
        details=card_data.details,
        position=max_position
    )
    db.add(card)
    db.commit()
    db.refresh(card)

    return CardOut.model_validate(card)


@app.put("/api/cards/{card_id}")
async def update_card(card_id: int, update: CardUpdate, token: str = Depends(require_auth), db: Session = Depends(get_db)):
    """Update a card"""
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    if update.title is not None:
        card.title = update.title
    if update.details is not None:
        card.details = update.details

    db.commit()
    db.refresh(card)

    return CardOut.model_validate(card)


@app.delete("/api/cards/{card_id}")
async def delete_card(card_id: int, token: str = Depends(require_auth), db: Session = Depends(get_db)):
    """Delete a card"""
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    column_id = card.column_id
    position = card.position

    db.delete(card)

    # Compact positions in the column
    cards_after = db.query(Card).filter(
        Card.column_id == column_id,
        Card.position > position
    ).order_by(Card.position).all()

    for i, c in enumerate(cards_after):
        c.position = position + i

    db.commit()

    return {"message": "Card deleted"}


@app.put("/api/cards/{card_id}/move")
async def move_card(card_id: int, move_data: CardMove, token: str = Depends(require_auth), db: Session = Depends(get_db)):
    """Move a card to a new column and position"""
    print(f"DEBUG: move_card called for card_id={card_id}, column_id={move_data.column_id}, position={move_data.position}")

    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        print(f"DEBUG: Card {card_id} not found")
        raise HTTPException(status_code=404, detail="Card not found")

    old_column_id = card.column_id
    old_position = card.position

    # Compact positions in old column
    if old_column_id != move_data.column_id or old_position != move_data.position:
        cards_after_old = db.query(Card).filter(
            Card.column_id == old_column_id,
            Card.position > old_position
        ).order_by(Card.position).all()

        for i, c in enumerate(cards_after_old):
            c.position = old_position + i

        # Shift positions in new column to make room
        cards_at_position = db.query(Card).filter(
            Card.column_id == move_data.column_id,
            Card.position >= move_data.position
        ).order_by(Card.position.desc()).all()

        for c in cards_at_position:
            c.position += 1

        # Update card
        card.column_id = move_data.column_id
        card.position = move_data.position

    db.commit()
    db.refresh(card)

    print(f"DEBUG: Card {card_id} moved to column {card.column_id} at position {card.position}")

    return CardOut.model_validate(card)


# Mount NextJS static assets
app.mount("/_next", StaticFiles(directory="static/_next"), name="next_static")

# Mount favicon and other public files
app.mount("/public", StaticFiles(directory="static"), name="public_files")

# Catch-all route handler for Next.js static export
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    # Serve static assets directly (files with extensions)
    if full_path and "." in full_path:
        return FileResponse(f"static/{full_path}")

    # Check for a page-specific index.html (e.g. /login -> static/login/index.html)
    if full_path:
        page_html = f"static/{full_path}/index.html"
        if os.path.isfile(page_html):
            return FileResponse(page_html)

    return FileResponse("static/index.html")


def start():
    """Entry point for uvicorn"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    start()

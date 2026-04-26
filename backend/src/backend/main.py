from datetime import datetime
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from sqlalchemy import func
import os
import secrets

from .database import Base, engine, get_db, SessionLocal
from .models import User, Board, Column as ColumnModel, Card
from .ai import call_ai, call_ai_with_context

app = FastAPI(title="Project Management MVP Backend")

# Hardcoded credentials for MVP
VALID_USERNAME = "user"
VALID_PASSWORD = "password"

# Simple in-memory token store (for MVP only - not production)
valid_tokens = set()


# Helper functions
def compact_column_positions(db: Session, column_id: int, after_position: int) -> None:
    cards_after = db.query(Card).filter(
        Card.column_id == column_id,
        Card.position > after_position,
    ).order_by(Card.position).all()
    for i, c in enumerate(cards_after):
        c.position = after_position + i


def get_user_board(db: Session) -> tuple[User, Board]:
    user = db.query(User).filter(User.username == VALID_USERNAME).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    board = db.query(Board).filter(Board.user_id == user.id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    return user, board


def serialize_board_for_ai(db: Session, columns: list[ColumnModel]) -> dict:
    return {
        "columns": [
            {
                "id": col.id,
                "title": col.title,
                "cards": [
                    {"id": c.id, "title": c.title, "details": c.details}
                    for c in db.query(Card).filter(Card.column_id == col.id).order_by(Card.position).all()
                ]
            }
            for col in columns
        ]
    }

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


class AIQueryRequest(BaseModel):
    question: str


class AIUpdate(BaseModel):
    action: str
    columnId: int | None = None
    cardId: int | None = None
    title: str | None = None
    details: str | None = None
    position: int | None = None


class AIQueryResponse(BaseModel):
    response: str
    updates: list[AIUpdate] = []
    board: BoardOut | None = None


def extract_bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    return authorization[7:]


def require_auth(authorization: str = Header(None)) -> str:
    """Validate Bearer token"""
    token = extract_bearer_token(authorization)
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
async def logout(token: str = Depends(require_auth)):
    """Logout and invalidate token"""
    valid_tokens.discard(token)
    return {"message": "Logged out successfully"}


@app.get("/api/verify")
async def verify(token: str = Depends(require_auth)):
    """Verify authentication token"""
    return {"status": "authenticated"}


@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "Backend is running"}


@app.post("/api/ai/test")
async def ai_test(token: str = Depends(require_auth)):
    """Test AI endpoint: calls OpenRouter with '2+2' and returns full response."""
    try:
        response = await call_ai("2+2")
        return response
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"AI call failed: {str(error)}")


@app.post("/api/ai/query", response_model=AIQueryResponse)
async def ai_query(
    request: AIQueryRequest,
    token: str = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Query AI with Kanban context and apply updates."""
    try:
        user, board = get_user_board(db)

        columns = db.query(ColumnModel).filter(ColumnModel.board_id == board.id).order_by(ColumnModel.position).all()
        board_data = serialize_board_for_ai(db, columns)

        # Call AI with context
        ai_response = await call_ai_with_context(board_data, request.question)

        # Apply updates
        updates = ai_response.get("updates", [])
        for update in updates:
            action = update.get("action")

            if action == "create_card":
                column_id = update.get("columnId")
                if not column_id:
                    continue
                max_pos = db.query(Card).filter(Card.column_id == column_id).count()
                card = Card(
                    column_id=column_id,
                    title=update.get("title", "Untitled"),
                    details=update.get("details", ""),
                    position=max_pos,
                )
                db.add(card)

            elif action == "edit_card":
                card_id = update.get("cardId")
                card = db.query(Card).filter(Card.id == card_id).first()
                if card:
                    if update.get("title"):
                        card.title = update.get("title")
                    if update.get("details") is not None:
                        card.details = update.get("details")

            elif action == "move_card":
                card_id = update.get("cardId")
                new_column_id = update.get("columnId")
                new_position = update.get("position", 0)

                card = db.query(Card).filter(Card.id == card_id).first()
                if card and new_column_id:
                    old_column_id = card.column_id
                    old_position = card.position

                    compact_column_positions(db, old_column_id, old_position)

                    cards_at_pos = db.query(Card).filter(
                        Card.column_id == new_column_id,
                        Card.position >= new_position,
                    ).order_by(Card.position.desc()).all()
                    for c in cards_at_pos:
                        c.position += 1

                    card.column_id = new_column_id
                    card.position = new_position

            elif action == "delete_card":
                card_id = update.get("cardId")
                card = db.query(Card).filter(Card.id == card_id).first()
                if card:
                    col_id = card.column_id
                    pos = card.position
                    db.delete(card)
                    compact_column_positions(db, col_id, pos)

        db.commit()

        # Fetch updated board
        columns = db.query(ColumnModel).filter(ColumnModel.board_id == board.id).order_by(ColumnModel.position).all()
        columns_data = []
        for col in columns:
            cards = db.query(Card).filter(Card.column_id == col.id).order_by(Card.position).all()
            columns_data.append(
                ColumnOut(
                    id=col.id,
                    title=col.title,
                    position=col.position,
                    cards=[CardOut.model_validate(c) for c in cards],
                )
            )

        updated_board = BoardOut(id=board.id, title=board.title, columns=columns_data)

        return AIQueryResponse(
            response=ai_response.get("response", ""),
            updates=updates,
            board=updated_board,
        )

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"AI query failed: {str(error)}")


# Kanban endpoints
@app.get("/api/board", response_model=BoardOut)
async def get_board(token: str = Depends(require_auth), db: Session = Depends(get_db)):
    """Get full board state with columns and cards"""
    user, board = get_user_board(db)

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

    max_pos = db.query(func.max(Card.position)).filter(Card.column_id == card_data.column_id).scalar() or -1

    card = Card(
        column_id=card_data.column_id,
        title=card_data.title,
        details=card_data.details,
        position=max_pos + 1
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
    compact_column_positions(db, column_id, position)
    db.commit()

    return {"message": "Card deleted"}


@app.put("/api/cards/{card_id}/move")
async def move_card(card_id: int, move_data: CardMove, token: str = Depends(require_auth), db: Session = Depends(get_db)):
    """Move a card to a new column and position"""
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    old_column_id = card.column_id
    old_position = card.position

    if old_column_id != move_data.column_id or old_position != move_data.position:
        compact_column_positions(db, old_column_id, old_position)

        cards_at_position = db.query(Card).filter(
            Card.column_id == move_data.column_id,
            Card.position >= move_data.position
        ).order_by(Card.position.desc()).all()

        for c in cards_at_position:
            c.position += 1

        card.column_id = move_data.column_id
        card.position = move_data.position

    db.commit()
    db.refresh(card)

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

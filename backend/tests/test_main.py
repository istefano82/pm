import pytest
from fastapi.testclient import TestClient
from src.backend.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Kanban Studio" in response.text

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Backend is running"}

def test_login_valid():
    response = client.post("/api/login", json={"username": "user", "password": "password"})
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["message"] == "Login successful"

def test_login_invalid_credentials():
    response = client.post("/api/login", json={"username": "wrong", "password": "wrong"})
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_verify_valid_token():
    # First login to get token
    login_response = client.post("/api/login", json={"username": "user", "password": "password"})
    token = login_response.json()["token"]
    
    # Then verify
    response = client.get("/api/verify", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["status"] == "authenticated"

def test_verify_invalid_token():
    response = client.get("/api/verify", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401

def test_logout():
    # Login first
    login_response = client.post("/api/login", json={"username": "user", "password": "password"})
    token = login_response.json()["token"]

    # Logout
    response = client.post("/api/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    # Token should be invalid now
    verify_response = client.get("/api/verify", headers={"Authorization": f"Bearer {token}"})
    assert verify_response.status_code == 401


def test_get_board_unauthenticated():
    response = client.get("/api/board")
    assert response.status_code == 401


def test_get_board():
    # Login first
    login_response = client.post("/api/login", json={"username": "user", "password": "password"})
    token = login_response.json()["token"]

    # Get board
    response = client.get("/api/board", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "My Project"
    assert len(data["columns"]) == 5
    # Don't check specific column title or card count as they may have been modified by other tests
    assert all("id" in col and "title" in col and "cards" in col for col in data["columns"])


def test_create_card():
    login_response = client.post("/api/login", json={"username": "user", "password": "password"})
    token = login_response.json()["token"]

    # Get board to find a column
    board_response = client.get("/api/board", headers={"Authorization": f"Bearer {token}"})
    board = board_response.json()
    column_id = board["columns"][0]["id"]
    initial_card_count = len(board["columns"][0]["cards"])

    # Create card
    response = client.post(
        "/api/cards",
        json={"column_id": column_id, "title": "Test Card", "details": "Test Details"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    card = response.json()
    assert card["title"] == "Test Card"
    assert card["details"] == "Test Details"

    # Verify card appears in board
    board_response = client.get("/api/board", headers={"Authorization": f"Bearer {token}"})
    board = board_response.json()
    assert len(board["columns"][0]["cards"]) == initial_card_count + 1


def test_update_card():
    login_response = client.post("/api/login", json={"username": "user", "password": "password"})
    token = login_response.json()["token"]

    # Get board to find a card
    board_response = client.get("/api/board", headers={"Authorization": f"Bearer {token}"})
    board = board_response.json()
    card = board["columns"][0]["cards"][0]
    card_id = card["id"]

    # Update card
    response = client.put(
        f"/api/cards/{card_id}",
        json={"title": "Updated Title", "details": "Updated Details"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == "Updated Title"
    assert updated["details"] == "Updated Details"


def test_delete_card():
    login_response = client.post("/api/login", json={"username": "user", "password": "password"})
    token = login_response.json()["token"]

    # Get board to find a card
    board_response = client.get("/api/board", headers={"Authorization": f"Bearer {token}"})
    board = board_response.json()
    card = board["columns"][0]["cards"][0]
    card_id = card["id"]
    initial_count = len(board["columns"][0]["cards"])

    # Delete card
    response = client.delete(
        f"/api/cards/{card_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    # Verify card is gone
    board_response = client.get("/api/board", headers={"Authorization": f"Bearer {token}"})
    board = board_response.json()
    assert len(board["columns"][0]["cards"]) == initial_count - 1


def test_rename_column():
    login_response = client.post("/api/login", json={"username": "user", "password": "password"})
    token = login_response.json()["token"]

    # Get board to find a column
    board_response = client.get("/api/board", headers={"Authorization": f"Bearer {token}"})
    board = board_response.json()
    column = board["columns"][0]
    column_id = column["id"]

    # Rename column
    response = client.put(
        f"/api/columns/{column_id}",
        json={"title": "New Title"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"

    # Verify in board
    board_response = client.get("/api/board", headers={"Authorization": f"Bearer {token}"})
    board = board_response.json()
    assert board["columns"][0]["title"] == "New Title"


def test_move_card():
    login_response = client.post("/api/login", json={"username": "user", "password": "password"})
    token = login_response.json()["token"]

    # Get board
    board_response = client.get("/api/board", headers={"Authorization": f"Bearer {token}"})
    board = board_response.json()

    # Find a column with cards to move from
    source_column = None
    card = None
    for col in board["columns"]:
        if col["cards"]:
            source_column = col
            card = col["cards"][0]
            break

    if not card:
        # Skip test if no cards available
        assert True
        return

    card_id = card["id"]

    # Get destination column
    dest_column = board["columns"][1]
    dest_column_id = dest_column["id"]
    dest_position = len(dest_column["cards"])

    # Move card
    response = client.put(
        f"/api/cards/{card_id}/move",
        json={"column_id": dest_column_id, "position": dest_position},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    moved_card = response.json()
    assert moved_card["position"] == dest_position

    # Verify in board
    board_response = client.get("/api/board", headers={"Authorization": f"Bearer {token}"})
    board = board_response.json()

    # Card should be in destination column
    dest_card_ids = [c["id"] for c in board["columns"][1]["cards"]]
    assert card_id in dest_card_ids


def test_ai_query():
    login_response = client.post("/api/login", json={"username": "user", "password": "password"})
    token = login_response.json()["token"]

    # Query AI
    response = client.post(
        "/api/ai/query",
        json={"question": "Create a card called Test"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "updates" in data
    assert "board" in data


def test_ai_test():
    login_response = client.post("/api/login", json={"username": "user", "password": "password"})
    token = login_response.json()["token"]
    response = client.post("/api/ai/test", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_missing_auth_header():
    response = client.get("/api/board")
    assert response.status_code == 401


def test_create_card_nonexistent_column():
    login_response = client.post("/api/login", json={"username": "user", "password": "password"})
    token = login_response.json()["token"]

    # Try to create card in nonexistent column
    response = client.post(
        "/api/cards",
        json={"column_id": 99999, "title": "Test", "details": "Test"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


def test_update_nonexistent_card():
    login_response = client.post("/api/login", json={"username": "user", "password": "password"})
    token = login_response.json()["token"]

    # Try to update nonexistent card
    response = client.put(
        "/api/cards/99999",
        json={"title": "Updated"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


def test_delete_nonexistent_card():
    login_response = client.post("/api/login", json={"username": "user", "password": "password"})
    token = login_response.json()["token"]

    # Try to delete nonexistent card
    response = client.delete(
        "/api/cards/99999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


def test_move_nonexistent_card():
    login_response = client.post("/api/login", json={"username": "user", "password": "password"})
    token = login_response.json()["token"]

    # Get board to find a valid column
    board_response = client.get("/api/board", headers={"Authorization": f"Bearer {token}"})
    board = board_response.json()
    column_id = board["columns"][0]["id"]

    # Try to move nonexistent card
    response = client.put(
        "/api/cards/99999/move",
        json={"column_id": column_id, "position": 0},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


def test_rename_nonexistent_column():
    login_response = client.post("/api/login", json={"username": "user", "password": "password"})
    token = login_response.json()["token"]

    # Try to rename nonexistent column
    response = client.put(
        "/api/columns/99999",
        json={"title": "New Title"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
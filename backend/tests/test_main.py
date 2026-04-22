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
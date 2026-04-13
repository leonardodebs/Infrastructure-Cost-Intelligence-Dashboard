import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_success():
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_username():
    response = client.post(
        "/auth/login",
        data={"username": "invalid", "password": "admin123"}
    )
    assert response.status_code == 401

def test_login_invalid_password():
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_get_current_user_unauthorized():
    response = client.get("/auth/me")
    assert response.status_code == 401

def test_get_current_user_authorized():
    login_response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    token = login_response.json()["access_token"]
    
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
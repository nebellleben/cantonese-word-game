import pytest
from fastapi.testclient import TestClient


def test_login_success(client):
    """Test successful login."""
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "cantonese"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "user" in data
    assert data["user"]["username"] == "admin"
    assert data["user"]["role"] == "admin"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_register_student(client):
    """Test student registration."""
    response = client.post(
        "/api/auth/register",
        json={"username": "newstudent", "password": "password123", "role": "student"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "token" in data
    assert "user" in data
    assert data["user"]["username"] == "newstudent"
    assert data["user"]["role"] == "student"


def test_register_teacher(client):
    """Test teacher registration."""
    response = client.post(
        "/api/auth/register",
        json={"username": "newteacher", "password": "password123", "role": "teacher"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["role"] == "teacher"


def test_register_duplicate_username(client):
    """Test registration with duplicate username."""
    # First registration
    client.post(
        "/api/auth/register",
        json={"username": "duplicate", "password": "pass", "role": "student"}
    )
    
    # Second registration with same username
    response = client.post(
        "/api/auth/register",
        json={"username": "duplicate", "password": "pass", "role": "student"}
    )
    assert response.status_code == 400



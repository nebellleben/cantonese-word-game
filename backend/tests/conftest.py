import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.mock_db import MockDatabase, db


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Create a fresh mock database for each test."""
    # Reset the global db instance
    db.__init__()
    return db


@pytest.fixture
def admin_token(client):
    """Get admin authentication token."""
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "cantonese"}
    )
    assert response.status_code == 200
    return response.json()["token"]


@pytest.fixture
def student_user(client):
    """Create a test student user and return token."""
    response = client.post(
        "/api/auth/register",
        json={"username": "teststudent", "password": "testpass", "role": "student"}
    )
    assert response.status_code == 201
    return response.json()["token"], response.json()["user"]


@pytest.fixture
def teacher_user(client):
    """Create a test teacher user and return token."""
    response = client.post(
        "/api/auth/register",
        json={"username": "testteacher", "password": "testpass", "role": "teacher"}
    )
    assert response.status_code == 201
    return response.json()["token"], response.json()["user"]


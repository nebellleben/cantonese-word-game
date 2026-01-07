"""
Pytest configuration for backend tests.
Uses a temporary SQLite database via SQLAlchemy for all tests.
"""
import os
import tempfile
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.db.base import Base, get_db
from app.main import app


@pytest.fixture(scope="session")
def test_db_path():
    """Create a temporary database file."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture(scope="session")
def test_engine(test_db_path):
    """Create a test database engine."""
    database_url = f"sqlite:///{test_db_path}"
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    # Enable foreign key support for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup: drop all tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db_session(test_engine):
    """Create a test database session for each test."""
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Ensure tables exist
    Base.metadata.create_all(bind=test_engine)

    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

        # Clean up all data after each test
        for table in reversed(Base.metadata.sorted_tables):
            cleanup_session = TestSessionLocal()
            try:
                cleanup_session.execute(table.delete())
                cleanup_session.commit()
            except Exception:
                cleanup_session.rollback()
            finally:
                cleanup_session.close()


@pytest.fixture(scope="function")
def client(test_db_session):
    """Create a test client with database dependency override."""

    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_user(test_db_session):
    """Create a default admin user in the test database."""
    from app.db.models import User
    from app.core.security import get_password_hash

    admin = User(
        username="admin",
        password_hash=get_password_hash("cantonese"),
        role="admin",
    )
    test_db_session.add(admin)
    test_db_session.commit()
    test_db_session.refresh(admin)
    return admin


@pytest.fixture
def admin_token(client, admin_user):
    """Get admin authentication token."""
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "cantonese"},
    )
    assert response.status_code == 200
    return response.json()["token"]


@pytest.fixture
def student_user(client):
    """Create a test student user and return token and user."""
    unique_username = f"teststudent_{uuid.uuid4().hex[:8]}"
    response = client.post(
        "/api/auth/register",
        json={"username": unique_username, "password": "testpass", "role": "student"},
    )
    assert response.status_code == 201
    return response.json()["token"], response.json()["user"]


@pytest.fixture
def teacher_user(client):
    """Create a test teacher user and return token and user."""
    unique_username = f"testteacher_{uuid.uuid4().hex[:8]}"
    response = client.post(
        "/api/auth/register",
        json={"username": unique_username, "password": "testpass", "role": "teacher"},
    )
    assert response.status_code == 201
    return response.json()["token"], response.json()["user"]



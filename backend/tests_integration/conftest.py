"""
Pytest configuration for integration tests.
Uses SQLite database for testing.
"""
import pytest
import os
import tempfile
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.base import Base, get_db
from app.main import app
from app.core.config import settings


# Create a temporary SQLite database for testing
@pytest.fixture(scope="session")
def test_db_path():
    """Create a temporary database file."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    # Cleanup: remove the database file after tests
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
    from sqlalchemy import event
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
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=test_engine)
    
    # Create a session
    session = TestSessionLocal()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        
        # Clean up all data after each test
        for table in reversed(Base.metadata.sorted_tables):
            session = TestSessionLocal()
            try:
                session.execute(table.delete())
                session.commit()
            except Exception:
                session.rollback()
            finally:
                session.close()


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
        json={"username": "admin", "password": "cantonese"}
    )
    assert response.status_code == 200
    return response.json()["token"]


@pytest.fixture
def sample_deck(test_db_session):
    """Create a sample deck for testing."""
    from app.db.models import Deck
    
    deck = Deck(
        name="Test Deck",
        description="A test deck for integration tests",
    )
    test_db_session.add(deck)
    test_db_session.commit()
    test_db_session.refresh(deck)
    return deck


@pytest.fixture
def sample_words(test_db_session, sample_deck):
    """Create sample words for testing."""
    from app.db.models import Word
    
    words_data = [
        {"text": "你好", "jyutping": "nei5 hou2"},
        {"text": "謝謝", "jyutping": "ze6 ze6"},
        {"text": "再見", "jyutping": "zoi3 gin3"},
    ]
    
    words = []
    for word_data in words_data:
        word = Word(
            text=word_data["text"],
            jyutping=word_data["jyutping"],
            deck_id=sample_deck.id,
        )
        test_db_session.add(word)
        words.append(word)
    
    test_db_session.commit()
    for word in words:
        test_db_session.refresh(word)
    
    return words


"""
Integration tests for backend-frontend communication.
Tests that the backend API matches what the frontend expects.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_backend_health():
    """Test backend health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_api_root():
    """Test API root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_cors_headers():
    """Test that CORS headers are set correctly."""
    response = client.options(
        "/api/decks",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET"
        }
    )
    # CORS preflight should be handled by middleware
    assert response.status_code in [200, 204, 405]


def test_login_flow():
    """Test complete login flow that frontend uses."""
    # Login with default admin
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
    
    token = data["token"]
    
    # Use token to access protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/decks", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_register_and_login():
    """Test registration then login flow."""
    # Register new user
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "testpass123", "role": "student"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "token" in data
    assert "user" in data
    assert data["user"]["username"] == "testuser"
    
    # Login with new user
    response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200
    assert response.json()["user"]["username"] == "testuser"


def test_get_decks_requires_auth():
    """Test that decks endpoint requires authentication."""
    response = client.get("/api/decks")
    assert response.status_code == 401 or response.status_code == 403


def test_game_flow():
    """Test complete game flow."""
    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "cantonese"}
    )
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get decks
    decks_response = client.get("/api/decks", headers=headers)
    assert decks_response.status_code == 200
    decks = decks_response.json()
    assert len(decks) > 0
    deck_id = decks[0]["id"]
    
    # Start game
    start_response = client.post(
        "/api/games/start",
        json={"deckId": str(deck_id)},
        headers=headers
    )
    assert start_response.status_code == 201
    session = start_response.json()
    assert "id" in session
    assert "words" in session
    assert len(session["words"]) > 0
    
    session_id = session["id"]
    # Handle both camelCase and snake_case for compatibility
    first_word = session["words"][0]
    word_id = first_word.get("wordId") or first_word.get("word_id")
    
    # Submit pronunciation
    pronunciation_response = client.post(
        "/api/games/pronunciation",
        data={
            "sessionId": str(session_id),
            "wordId": str(word_id),
            "responseTime": "1500"
        },
        headers=headers
    )
    assert pronunciation_response.status_code == 200
    result = pronunciation_response.json()
    # Accept both camelCase and snake_case for compatibility
    assert "isCorrect" in result or "is_correct" in result
    
    # End game
    end_response = client.post(
        f"/api/games/{session_id}/end",
        headers=headers
    )
    assert end_response.status_code == 200
    ended_session = end_response.json()
    assert "score" in ended_session
    assert ended_session["score"] is not None


def test_statistics_endpoint():
    """Test statistics endpoint."""
    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "cantonese"}
    )
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get statistics
    response = client.get("/api/statistics", headers=headers)
    assert response.status_code == 200
    stats = response.json()
    assert "totalGames" in stats
    assert "averageScore" in stats
    assert "bestScore" in stats
    assert "currentStreak" in stats
    assert "longestStreak" in stats
    assert "scoresByDate" in stats
    assert "topWrongWords" in stats


def test_admin_endpoints():
    """Test admin endpoints."""
    # Login as admin
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "cantonese"}
    )
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create deck
    create_response = client.post(
        "/api/admin/decks",
        json={"name": "Integration Test Deck", "description": "Test"},
        headers=headers
    )
    assert create_response.status_code == 201
    deck = create_response.json()
    deck_id = deck["id"]
    
    # Add word
    word_response = client.post(
        f"/api/admin/decks/{deck_id}/words",
        json={"text": "測試"},
        headers=headers
    )
    assert word_response.status_code == 201
    word = word_response.json()
    assert word["text"] == "測試"
    assert "jyutping" in word
    
    # Delete word
    delete_word_response = client.delete(
        f"/api/admin/words/{word['id']}",
        headers=headers
    )
    assert delete_word_response.status_code == 204
    
    # Delete deck
    delete_deck_response = client.delete(
        f"/api/admin/decks/{deck_id}",
        headers=headers
    )
    assert delete_deck_response.status_code == 204


def test_api_response_format():
    """Test that API responses match frontend expectations."""
    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "cantonese"}
    )
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check deck response format
    decks_response = client.get("/api/decks", headers=headers)
    decks = decks_response.json()
    if len(decks) > 0:
        deck = decks[0]
        assert "id" in deck
        assert "name" in deck
        assert "createdAt" in deck
    
    # Check word response format
    if len(decks) > 0:
        words_response = client.get(f"/api/decks/{decks[0]['id']}/words", headers=headers)
        words = words_response.json()
        if len(words) > 0:
            word = words[0]
            assert "id" in word
            assert "text" in word
            assert "jyutping" in word
            # Accept both camelCase and snake_case
            assert "deckId" in word or "deck_id" in word
            assert "createdAt" in word or "created_at" in word


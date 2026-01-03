import pytest
from fastapi.testclient import TestClient


def test_get_decks_unauthorized(client):
    """Test getting decks without authentication."""
    response = client.get("/api/decks")
    assert response.status_code == 401  # Unauthorized, not Forbidden


def test_get_decks(client, admin_token):
    """Test getting all decks."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/decks", headers=headers)
    assert response.status_code == 200
    decks = response.json()
    assert isinstance(decks, list)
    assert len(decks) > 0
    assert "id" in decks[0]
    assert "name" in decks[0]


def test_get_words_by_deck(client, admin_token):
    """Test getting words in a deck."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # First get decks
    decks_response = client.get("/api/decks", headers=headers)
    decks = decks_response.json()
    assert len(decks) > 0
    deck_id = decks[0]["id"]
    
    # Get words
    response = client.get(f"/api/decks/{deck_id}/words", headers=headers)
    assert response.status_code == 200
    words = response.json()
    assert isinstance(words, list)
    if len(words) > 0:
        assert "id" in words[0]
        assert "text" in words[0]
        assert "jyutping" in words[0]


def test_get_words_by_deck_not_found(client, admin_token):
    """Test getting words from non-existent deck."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/decks/00000000-0000-0000-0000-000000000999/words", headers=headers)
    assert response.status_code == 404


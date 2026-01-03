import pytest
from fastapi.testclient import TestClient


def test_create_deck(client, admin_token):
    """Test creating a deck."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.post(
        "/api/admin/decks",
        json={"name": "Test Deck", "description": "Test description"},
        headers=headers
    )
    assert response.status_code == 201
    deck = response.json()
    assert deck["name"] == "Test Deck"
    assert deck["description"] == "Test description"
    assert "id" in deck


def test_delete_deck(client, admin_token):
    """Test deleting a deck."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Create a deck first
    create_response = client.post(
        "/api/admin/decks",
        json={"name": "To Delete", "description": "Will be deleted"},
        headers=headers
    )
    deck_id = create_response.json()["id"]
    
    # Delete it
    response = client.delete(f"/api/admin/decks/{deck_id}", headers=headers)
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get("/api/decks", headers=headers)
    decks = get_response.json()
    assert deck_id not in [d["id"] for d in decks]


def test_add_word(client, admin_token):
    """Test adding a word to a deck."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get or create a deck
    decks_response = client.get("/api/decks", headers=headers)
    decks = decks_response.json()
    deck_id = decks[0]["id"]
    
    # Add word
    response = client.post(
        f"/api/admin/decks/{deck_id}/words",
        json={"text": "測試"},
        headers=headers
    )
    assert response.status_code == 201
    word = response.json()
    assert word["text"] == "測試"
    assert "jyutping" in word
    assert word["deckId"] == deck_id


def test_delete_word(client, admin_token):
    """Test deleting a word."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get a deck and add a word
    decks_response = client.get("/api/decks", headers=headers)
    decks = decks_response.json()
    deck_id = decks[0]["id"]
    
    add_response = client.post(
        f"/api/admin/decks/{deck_id}/words",
        json={"text": "刪除測試"},
        headers=headers
    )
    word_id = add_response.json()["id"]
    
    # Delete word
    response = client.delete(f"/api/admin/words/{word_id}", headers=headers)
    assert response.status_code == 204


def test_admin_only_endpoints(client, student_user):
    """Test that admin endpoints require admin role."""
    token, _ = student_user
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to create deck as student
    response = client.post(
        "/api/admin/decks",
        json={"name": "Test", "description": "Test"},
        headers=headers
    )
    assert response.status_code == 403


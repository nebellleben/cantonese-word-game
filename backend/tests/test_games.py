import pytest
from fastapi.testclient import TestClient


def test_start_game(client, student_user):
    """Test starting a game."""
    token, user = student_user
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get a deck first
    decks_response = client.get("/api/decks", headers=headers)
    decks = decks_response.json()
    assert len(decks) > 0
    deck_id = decks[0]["id"]
    
    # Start game
    response = client.post(
        "/api/games/start",
        json={"deckId": deck_id},
        headers=headers
    )
    assert response.status_code == 201
    session = response.json()
    assert "id" in session
    assert "words" in session
    assert len(session["words"]) > 0
    assert session["userId"] == user["id"]


def test_submit_pronunciation(client, student_user):
    """Test submitting pronunciation."""
    token, user = student_user
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get a deck and start game
    decks_response = client.get("/api/decks", headers=headers)
    decks = decks_response.json()
    deck_id = decks[0]["id"]
    
    start_response = client.post(
        "/api/games/start",
        json={"deckId": deck_id},
        headers=headers
    )
    session = start_response.json()
    session_id = session["id"]
    word_id = session["words"][0]["wordId"]
    
    # Submit pronunciation
    response = client.post(
        "/api/games/pronunciation",
        data={
            "sessionId": str(session_id),
            "wordId": str(word_id),
            "responseTime": "1500"
        },
        headers=headers
    )
    assert response.status_code == 200
    result = response.json()
    assert "isCorrect" in result


def test_end_game(client, student_user):
    """Test ending a game."""
    token, user = student_user
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get a deck and start game
    decks_response = client.get("/api/decks", headers=headers)
    decks = decks_response.json()
    deck_id = decks[0]["id"]
    
    start_response = client.post(
        "/api/games/start",
        json={"deckId": deck_id},
        headers=headers
    )
    session = start_response.json()
    session_id = session["id"]
    
    # Submit a pronunciation
    word_id = session["words"][0]["wordId"]
    client.post(
        "/api/games/pronunciation",
        data={
            "sessionId": str(session_id),
            "wordId": str(word_id),
            "responseTime": "1500"
        },
        headers=headers
    )
    
    # End game
    response = client.post(
        f"/api/games/{session_id}/end",
        headers=headers
    )
    assert response.status_code == 200
    ended_session = response.json()
    assert "score" in ended_session
    assert ended_session["score"] is not None
    assert "endedAt" in ended_session


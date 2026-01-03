"""
Integration tests for database operations through the API.
Tests that the API correctly interacts with the database.
"""
import pytest
from app.db.models import User, Deck, Word, GameSession, GameAttempt
from app.core.security import verify_password


def test_user_registration_persists(client, test_db_session):
    """Test that user registration persists to database."""
    username = "newuser123"
    password = "testpass123"
    
    # Register user through API
    response = client.post(
        "/api/auth/register",
        json={"username": username, "password": password, "role": "student"}
    )
    assert response.status_code == 201
    user_data = response.json()["user"]
    user_id = user_data["id"]
    
    # Verify user exists in database
    user = test_db_session.query(User).filter(User.id == user_id).first()
    assert user is not None
    assert user.username == username
    assert verify_password(password, user.password_hash)
    assert user.role == "student"


def test_user_login_with_database(client, test_db_session):
    """Test that login works with database users."""
    from app.core.security import get_password_hash
    
    # Create user directly in database
    user = User(
        username="dbloginuser",
        password_hash=get_password_hash("testpass"),
        role="student",
    )
    test_db_session.add(user)
    test_db_session.commit()
    
    # Login through API
    response = client.post(
        "/api/auth/login",
        json={"username": "dbloginuser", "password": "testpass"}
    )
    assert response.status_code == 200
    assert response.json()["user"]["username"] == "dbloginuser"


def test_create_deck_persists(client, admin_token, test_db_session):
    """Test that creating a deck persists to database."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = client.post(
        "/api/admin/decks",
        json={"name": "Database Test Deck", "description": "Test"},
        headers=headers
    )
    assert response.status_code == 201
    deck_data = response.json()
    deck_id = deck_data["id"]
    
    # Verify deck exists in database
    deck = test_db_session.query(Deck).filter(Deck.id == deck_id).first()
    assert deck is not None
    assert deck.name == "Database Test Deck"
    assert deck.description == "Test"


def test_add_word_persists(client, admin_token, sample_deck, test_db_session):
    """Test that adding a word persists to database."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = client.post(
        f"/api/admin/decks/{sample_deck.id}/words",
        json={"text": "數據庫"},
        headers=headers
    )
    assert response.status_code == 201
    word_data = response.json()
    word_id = word_data["id"]
    
    # Verify word exists in database
    word = test_db_session.query(Word).filter(Word.id == word_id).first()
    assert word is not None
    assert word.text == "數據庫"
    assert word.jyutping is not None  # Should be auto-generated
    assert word.deck_id == sample_deck.id


def test_game_session_persists(client, admin_token, sample_deck, sample_words, test_db_session):
    """Test that game session persists to database."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Start game
    response = client.post(
        "/api/games/start",
        json={"deckId": str(sample_deck.id)},
        headers=headers
    )
    assert response.status_code == 201
    session_data = response.json()
    session_id = session_data["id"]
    
    # Verify session exists in database
    session = test_db_session.query(GameSession).filter(GameSession.id == session_id).first()
    assert session is not None
    assert session.user_id is not None
    assert session.deck_id == sample_deck.id
    assert session.score is None  # Not ended yet
    assert session.ended_at is None


def test_game_attempt_persists(client, admin_token, sample_deck, sample_words, test_db_session):
    """Test that game attempt persists to database."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Start game
    start_response = client.post(
        "/api/games/start",
        json={"deckId": str(sample_deck.id)},
        headers=headers
    )
    session_id = start_response.json()["id"]
    word_id = start_response.json()["words"][0].get("wordId") or start_response.json()["words"][0].get("word_id")
    
    # Submit pronunciation
    attempt_response = client.post(
        "/api/games/pronunciation",
        data={
            "sessionId": str(session_id),
            "wordId": str(word_id),
            "responseTime": "2000"
        },
        headers=headers
    )
    assert attempt_response.status_code == 200
    
    # Verify attempt exists in database
    attempts = test_db_session.query(GameAttempt).filter(
        GameAttempt.session_id == session_id
    ).all()
    assert len(attempts) == 1
    assert attempts[0].word_id == word_id
    assert attempts[0].response_time == 2000
    assert attempts[0].is_correct is not None


def test_end_game_updates_session(client, admin_token, sample_deck, sample_words, test_db_session):
    """Test that ending a game updates the session in database."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Start game
    start_response = client.post(
        "/api/games/start",
        json={"deckId": str(sample_deck.id)},
        headers=headers
    )
    session_id = start_response.json()["id"]
    
    # Submit a few attempts
    for word in start_response.json()["words"][:2]:
        word_id = word.get("wordId") or word.get("word_id")
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
    end_response = client.post(
        f"/api/games/{session_id}/end",
        headers=headers
    )
    assert end_response.status_code == 200
    assert end_response.json()["score"] is not None
    
    # Verify session is updated in database
    session = test_db_session.query(GameSession).filter(GameSession.id == session_id).first()
    assert session.score is not None
    assert session.ended_at is not None


def test_delete_deck_cascades(client, admin_token, sample_deck, sample_words, test_db_session):
    """Test that deleting a deck cascades to words."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Verify words exist
    word_count = test_db_session.query(Word).filter(Word.deck_id == sample_deck.id).count()
    assert word_count == len(sample_words)
    
    # Delete deck
    response = client.delete(
        f"/api/admin/decks/{sample_deck.id}",
        headers=headers
    )
    assert response.status_code == 204
    
    # Verify words are deleted
    word_count = test_db_session.query(Word).filter(Word.deck_id == sample_deck.id).count()
    assert word_count == 0
    
    # Verify deck is deleted
    deck = test_db_session.query(Deck).filter(Deck.id == sample_deck.id).first()
    assert deck is None


def test_statistics_from_database(client, admin_token, sample_deck, sample_words, test_db_session):
    """Test that statistics are calculated from database."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Play a few games
    for _ in range(2):
        start_response = client.post(
            "/api/games/start",
            json={"deckId": str(sample_deck.id)},
            headers=headers
        )
        session_id = start_response.json()["id"]
        
        # Submit attempts for all words
        for word in start_response.json()["words"]:
            word_id = word.get("wordId") or word.get("word_id")
            client.post(
                "/api/games/pronunciation",
                data={
                    "sessionId": str(session_id),
                    "wordId": str(word_id),
                    "responseTime": "1000"
                },
                headers=headers
            )
        
        # End game
        client.post(
            f"/api/games/{session_id}/end",
            headers=headers
        )
    
    # Get statistics
    stats_response = client.get("/api/statistics", headers=headers)
    assert stats_response.status_code == 200
    stats = stats_response.json()
    
    # Verify statistics are calculated from database
    assert stats["totalGames"] == 2
    assert stats["averageScore"] is not None
    assert stats["bestScore"] is not None


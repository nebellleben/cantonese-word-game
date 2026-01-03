"""
Integration tests for database models.
Tests CRUD operations on database models.
"""
import pytest
from datetime import datetime, date
from app.db.models import User, Deck, Word, GameSession, GameAttempt, StudentTeacherAssociation, UserStreak
from app.core.security import get_password_hash


def test_create_user(test_db_session):
    """Test creating a user."""
    user = User(
        username="testuser",
        password_hash=get_password_hash("password123"),
        role="student",
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    
    assert user.id is not None
    assert user.username == "testuser"
    assert user.role == "student"
    assert user.created_at is not None


def test_create_deck(test_db_session):
    """Test creating a deck."""
    deck = Deck(
        name="Test Deck",
        description="Test description",
    )
    test_db_session.add(deck)
    test_db_session.commit()
    test_db_session.refresh(deck)
    
    assert deck.id is not None
    assert deck.name == "Test Deck"
    assert deck.description == "Test description"


def test_create_word(test_db_session, sample_deck):
    """Test creating a word."""
    word = Word(
        text="你好",
        jyutping="nei5 hou2",
        deck_id=sample_deck.id,
    )
    test_db_session.add(word)
    test_db_session.commit()
    test_db_session.refresh(word)
    
    assert word.id is not None
    assert word.text == "你好"
    assert word.jyutping == "nei5 hou2"
    assert word.deck_id == sample_deck.id


def test_create_game_session(test_db_session, admin_user, sample_deck):
    """Test creating a game session."""
    session = GameSession(
        user_id=admin_user.id,
        deck_id=sample_deck.id,
    )
    test_db_session.add(session)
    test_db_session.commit()
    test_db_session.refresh(session)
    
    assert session.id is not None
    assert session.user_id == admin_user.id
    assert session.deck_id == sample_deck.id
    assert session.score is None
    assert session.ended_at is None


def test_create_game_attempt(test_db_session, admin_user, sample_deck, sample_words):
    """Test creating a game attempt."""
    # Create a session first
    session = GameSession(
        user_id=admin_user.id,
        deck_id=sample_deck.id,
    )
    test_db_session.add(session)
    test_db_session.commit()
    test_db_session.refresh(session)
    
    # Create an attempt
    attempt = GameAttempt(
        session_id=session.id,
        word_id=sample_words[0].id,
        is_correct=True,
        response_time=1500,
    )
    test_db_session.add(attempt)
    test_db_session.commit()
    test_db_session.refresh(attempt)
    
    assert attempt.id is not None
    assert attempt.session_id == session.id
    assert attempt.word_id == sample_words[0].id
    assert attempt.is_correct is True
    assert attempt.response_time == 1500


def test_student_teacher_association(test_db_session):
    """Test creating student-teacher association."""
    student = User(
        username="student1",
        password_hash=get_password_hash("pass"),
        role="student",
    )
    teacher = User(
        username="teacher1",
        password_hash=get_password_hash("pass"),
        role="teacher",
    )
    test_db_session.add(student)
    test_db_session.add(teacher)
    test_db_session.commit()
    test_db_session.refresh(student)
    test_db_session.refresh(teacher)
    
    association = StudentTeacherAssociation(
        student_id=student.id,
        teacher_id=teacher.id,
    )
    test_db_session.add(association)
    test_db_session.commit()
    test_db_session.refresh(association)
    
    assert association.id is not None
    assert association.student_id == student.id
    assert association.teacher_id == teacher.id


def test_user_streak(test_db_session, admin_user):
    """Test creating user streak."""
    streak = UserStreak(
        user_id=admin_user.id,
        date=date.today(),
        games_completed=1,
    )
    test_db_session.add(streak)
    test_db_session.commit()
    test_db_session.refresh(streak)
    
    assert streak.id is not None
    assert streak.user_id == admin_user.id
    assert streak.date == date.today()
    assert streak.games_completed == 1


def test_foreign_key_constraints(test_db_session, sample_deck):
    """Test that foreign key constraints work."""
    # Try to create a word with invalid deck_id
    word = Word(
        text="測試",
        jyutping="ci3 si3",
        deck_id="invalid-uuid",
    )
    test_db_session.add(word)
    
    # Should raise an error on commit
    with pytest.raises(Exception):
        test_db_session.commit()


def test_unique_constraints(test_db_session):
    """Test unique constraints."""
    # Create first user
    user1 = User(
        username="uniqueuser",
        password_hash=get_password_hash("pass"),
        role="student",
    )
    test_db_session.add(user1)
    test_db_session.commit()
    
    # Try to create another user with same username
    user2 = User(
        username="uniqueuser",
        password_hash=get_password_hash("pass"),
        role="student",
    )
    test_db_session.add(user2)
    
    # Should raise an error on commit
    with pytest.raises(Exception):
        test_db_session.commit()


def test_cascade_delete(test_db_session, sample_deck, sample_words):
    """Test cascade delete behavior."""
    # Delete the deck
    test_db_session.delete(sample_deck)
    test_db_session.commit()
    
    # Words should be deleted too
    word_count = test_db_session.query(Word).filter(Word.deck_id == sample_deck.id).count()
    assert word_count == 0


def test_relationships(test_db_session, admin_user, sample_deck, sample_words):
    """Test SQLAlchemy relationships."""
    # Create a game session
    session = GameSession(
        user_id=admin_user.id,
        deck_id=sample_deck.id,
    )
    test_db_session.add(session)
    test_db_session.commit()
    test_db_session.refresh(session)
    
    # Test relationships
    assert session.user.id == admin_user.id
    assert session.deck.id == sample_deck.id
    
    # Create an attempt
    attempt = GameAttempt(
        session_id=session.id,
        word_id=sample_words[0].id,
        is_correct=True,
        response_time=1000,
    )
    test_db_session.add(attempt)
    test_db_session.commit()
    test_db_session.refresh(attempt)
    
    # Test relationships
    assert attempt.session.id == session.id
    assert attempt.word.id == sample_words[0].id
    assert len(session.game_attempts) == 1
    assert len(sample_words[0].game_attempts) == 1


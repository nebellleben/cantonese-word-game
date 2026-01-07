"""
Database service layer that provides database operations using SQLAlchemy.
This replaces mock_db and provides the same interface for services.
"""
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.db.models import (
    User, Deck, Word, GameSession, GameAttempt,
    StudentTeacherAssociation, UserStreak
)
from app.core.security import get_password_hash, verify_password


class DatabaseService:
    """Service for database operations using SQLAlchemy."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # User operations
    def get_user_by_id(self, user_id: UUID) -> Optional[Dict]:
        """Get user by ID."""
        user = self.db.query(User).filter(User.id == str(user_id)).first()
        if not user:
            return None
        return {
            "id": UUID(user.id),
            "username": user.username,
            "password_hash": user.password_hash,
            "role": user.role,
            "created_at": user.created_at,
        }
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username."""
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            return None
        return {
            "id": UUID(user.id),
            "username": user.username,
            "password_hash": user.password_hash,
            "role": user.role,
            "created_at": user.created_at,
        }
    
    def create_user(self, username: str, password: str, role: str) -> Dict:
        """Create a new user."""
        # Check if username already exists
        if self.get_user_by_username(username):
            raise ValueError("Username already exists")
        
        password_hash = get_password_hash(password)
        user = User(
            username=username,
            password_hash=password_hash,
            role=role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return {
            "id": UUID(user.id),
            "username": user.username,
            "password_hash": user.password_hash,
            "role": user.role,
            "created_at": user.created_at,
        }
    
    def reset_user_password(self, user_id: UUID, new_password: str) -> bool:
        """Reset user password."""
        user = self.db.query(User).filter(User.id == str(user_id)).first()
        if not user:
            return False
        
        user.password_hash = get_password_hash(new_password)
        self.db.commit()
        return True
    
    # Deck operations
    def get_deck(self, deck_id: UUID) -> Optional[Dict]:
        """Get deck by ID."""
        deck = self.db.query(Deck).filter(Deck.id == str(deck_id)).first()
        if not deck:
            return None
        return {
            "id": UUID(deck.id),
            "name": deck.name,
            "description": deck.description,
            "created_at": deck.created_at,
        }
    
    def get_all_decks(self) -> List[Dict]:
        """Get all decks."""
        # Include word counts for each deck so the frontend can display them
        decks = (
            self.db.query(
                Deck.id,
                Deck.name,
                Deck.description,
                Deck.created_at,
                func.count(Word.id).label("word_count"),
            )
            .outerjoin(Word, Word.deck_id == Deck.id)
            .group_by(Deck.id)
            .all()
        )

        return [
            {
                "id": UUID(deck.id),
                "name": deck.name,
                "description": deck.description,
                "created_at": deck.created_at,
                "word_count": deck.word_count,
            }
            for deck in decks
        ]
    
    def create_deck(self, name: str, description: Optional[str] = None) -> Dict:
        """Create a new deck."""
        deck = Deck(name=name, description=description)
        self.db.add(deck)
        self.db.commit()
        self.db.refresh(deck)
        
        return {
            "id": UUID(deck.id),
            "name": deck.name,
            "description": deck.description,
            "created_at": deck.created_at,
            "word_count": 0,
        }
    
    def delete_deck(self, deck_id: UUID) -> bool:
        """Delete a deck (cascade will delete words)."""
        deck = self.db.query(Deck).filter(Deck.id == str(deck_id)).first()
        if not deck:
            return False
        
        self.db.delete(deck)
        self.db.commit()
        return True
    
    # Word operations
    def get_word(self, word_id: UUID) -> Optional[Dict]:
        """Get word by ID."""
        word = self.db.query(Word).filter(Word.id == str(word_id)).first()
        if not word:
            return None
        return {
            "id": UUID(word.id),
            "text": word.text,
            "jyutping": word.jyutping,
            "deck_id": UUID(word.deck_id),
            "created_at": word.created_at,
        }
    
    def get_words_by_deck(self, deck_id: UUID) -> List[Dict]:
        """Get all words in a deck."""
        words = self.db.query(Word).filter(Word.deck_id == str(deck_id)).all()
        return [
            {
                "id": UUID(word.id),
                "text": word.text,
                "jyutping": word.jyutping,
                "deck_id": UUID(word.deck_id),
                "created_at": word.created_at,
            }
            for word in words
        ]
    
    def create_word(self, text: str, jyutping: str, deck_id: UUID) -> Dict:
        """Create a new word."""
        word = Word(
            text=text,
            jyutping=jyutping,
            deck_id=str(deck_id),
        )
        self.db.add(word)
        self.db.commit()
        self.db.refresh(word)
        
        return {
            "id": UUID(word.id),
            "text": word.text,
            "jyutping": word.jyutping,
            "deck_id": UUID(word.deck_id),
            "created_at": word.created_at,
        }
    
    def delete_word(self, word_id: UUID) -> bool:
        """Delete a word."""
        word = self.db.query(Word).filter(Word.id == str(word_id)).first()
        if not word:
            return False
        
        self.db.delete(word)
        self.db.commit()
        return True
    
    # Game session operations
    def get_game_session(self, session_id: UUID) -> Optional[Dict]:
        """Get game session by ID."""
        session = self.db.query(GameSession).filter(GameSession.id == str(session_id)).first()
        if not session:
            return None
        
        # Get word IDs from attempts
        attempts = self.db.query(GameAttempt).filter(GameAttempt.session_id == str(session_id)).all()
        word_ids = [UUID(attempt.word_id) for attempt in attempts]
        
        return {
            "id": UUID(session.id),
            "user_id": UUID(session.user_id),
            "deck_id": UUID(session.deck_id),
            "word_ids": word_ids,
            "score": session.score,
            "started_at": session.started_at,
            "ended_at": session.ended_at,
        }
    
    def create_game_session(self, user_id: UUID, deck_id: UUID, word_ids: List[UUID]) -> Dict:
        """Create a new game session."""
        session = GameSession(
            user_id=str(user_id),
            deck_id=str(deck_id),
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        # Create placeholder attempts for each word (will be updated when pronunciation is submitted)
        for word_id in word_ids:
            attempt = GameAttempt(
                session_id=session.id,
                word_id=str(word_id),
                is_correct=False,  # Placeholder, will be updated
                response_time=0,  # Placeholder
            )
            self.db.add(attempt)
        
        self.db.commit()
        
        return {
            "id": UUID(session.id),
            "user_id": UUID(session.user_id),
            "deck_id": UUID(session.deck_id),
            "word_ids": word_ids,
            "score": None,
            "started_at": session.started_at,
            "ended_at": None,
        }
    
    def update_game_session(self, session_id: UUID, score: Optional[int] = None, ended_at: Optional[datetime] = None):
        """Update game session."""
        session = self.db.query(GameSession).filter(GameSession.id == str(session_id)).first()
        if not session:
            return
        
        if score is not None:
            session.score = score
        if ended_at is not None:
            session.ended_at = ended_at
        
        self.db.commit()
    
    # Game attempt operations
    def create_game_attempt(self, session_id: UUID, word_id: UUID, is_correct: bool, response_time: int) -> Dict:
        """Create or update a game attempt record."""
        # Check if attempt already exists (from placeholder)
        attempt = self.db.query(GameAttempt).filter(
            and_(
                GameAttempt.session_id == str(session_id),
                GameAttempt.word_id == str(word_id)
            )
        ).first()
        
        if attempt:
            # Update existing attempt
            attempt.is_correct = is_correct
            attempt.response_time = response_time
            attempt.attempted_at = datetime.utcnow()
        else:
            # Create new attempt
            attempt = GameAttempt(
                session_id=str(session_id),
                word_id=str(word_id),
                is_correct=is_correct,
                response_time=response_time,
            )
            self.db.add(attempt)
        
        self.db.commit()
        self.db.refresh(attempt)
        
        return {
            "id": UUID(attempt.id),
            "session_id": UUID(attempt.session_id),
            "word_id": UUID(attempt.word_id),
            "is_correct": attempt.is_correct,
            "response_time": attempt.response_time,
            "attempted_at": attempt.attempted_at,
        }
    
    def get_attempts_by_session(self, session_id: UUID) -> List[Dict]:
        """Get all attempts for a session."""
        attempts = self.db.query(GameAttempt).filter(GameAttempt.session_id == str(session_id)).all()
        return [
            {
                "id": UUID(attempt.id),
                "session_id": UUID(attempt.session_id),
                "word_id": UUID(attempt.word_id),
                "is_correct": attempt.is_correct,
                "response_time": attempt.response_time,
                "attempted_at": attempt.attempted_at,
            }
            for attempt in attempts
        ]
    
    def get_attempts_by_user(self, user_id: UUID, deck_id: Optional[UUID] = None) -> List[Dict]:
        """Get all attempts for a user."""
        query = self.db.query(GameAttempt).join(GameSession).filter(GameSession.user_id == str(user_id))
        
        if deck_id:
            query = query.filter(GameSession.deck_id == str(deck_id))
        
        attempts = query.all()
        return [
            {
                "id": UUID(attempt.id),
                "session_id": UUID(attempt.session_id),
                "word_id": UUID(attempt.word_id),
                "is_correct": attempt.is_correct,
                "response_time": attempt.response_time,
                "attempted_at": attempt.attempted_at,
            }
            for attempt in attempts
        ]
    
    def get_attempts_by_students(self, student_ids: List[UUID]) -> List[Dict]:
        """Get all attempts for a list of students."""
        student_id_strs = [str(sid) for sid in student_ids]
        attempts = self.db.query(GameAttempt).join(GameSession).filter(
            GameSession.user_id.in_(student_id_strs)
        ).all()
        
        return [
            {
                "id": UUID(attempt.id),
                "session_id": UUID(attempt.session_id),
                "word_id": UUID(attempt.word_id),
                "is_correct": attempt.is_correct,
                "response_time": attempt.response_time,
                "attempted_at": attempt.attempted_at,
            }
            for attempt in attempts
        ]
    
    # Student-Teacher association operations
    def create_association(self, student_id: UUID, teacher_id: UUID):
        """Create student-teacher association."""
        # Check if association already exists
        existing = self.db.query(StudentTeacherAssociation).filter(
            and_(
                StudentTeacherAssociation.student_id == str(student_id),
                StudentTeacherAssociation.teacher_id == str(teacher_id)
            )
        ).first()
        
        if existing:
            return
        
        association = StudentTeacherAssociation(
            student_id=str(student_id),
            teacher_id=str(teacher_id),
        )
        self.db.add(association)
        self.db.commit()
    
    def get_students_by_teacher(self, teacher_id: UUID) -> List[UUID]:
        """Get all student IDs associated with a teacher."""
        associations = self.db.query(StudentTeacherAssociation).filter(
            StudentTeacherAssociation.teacher_id == str(teacher_id)
        ).all()
        
        return [UUID(assoc.student_id) for assoc in associations]
    
    def get_all_students(self) -> List[Dict]:
        """Get all students."""
        users = self.db.query(User).filter(User.role == "student").all()
        return [
            {
                "id": UUID(user.id),
                "username": user.username,
                "password_hash": user.password_hash,
                "role": user.role,
                "created_at": user.created_at,
            }
            for user in users
        ]
    
    def get_all_teachers(self) -> List[Dict]:
        """Get all teachers."""
        users = self.db.query(User).filter(User.role == "teacher").all()
        return [
            {
                "id": UUID(user.id),
                "username": user.username,
                "password_hash": user.password_hash,
                "role": user.role,
                "created_at": user.created_at,
            }
            for user in users
        ]
    
    # User streak operations
    def update_user_streak(self, user_id: UUID, game_date: date):
        """Update user streak for a given date."""
        # Get or create streak record for this date
        streak = self.db.query(UserStreak).filter(
            and_(
                UserStreak.user_id == str(user_id),
                UserStreak.date == game_date
            )
        ).first()
        
        if streak:
            streak.games_completed += 1
        else:
            # Get previous streak to calculate current streak
            previous_streaks = self.db.query(UserStreak).filter(
                UserStreak.user_id == str(user_id)
            ).order_by(UserStreak.date.desc()).all()
            
            current_streak = 1
            if previous_streaks:
                last_date = previous_streaks[0].date
                if (game_date - last_date).days == 1:
                    # Consecutive day - need to calculate from all streaks
                    consecutive_days = 1
                    for i in range(len(previous_streaks) - 1):
                        if (previous_streaks[i].date - previous_streaks[i + 1].date).days == 1:
                            consecutive_days += 1
                        else:
                            break
                    current_streak = consecutive_days + 1
            
            streak = UserStreak(
                user_id=str(user_id),
                date=game_date,
                games_completed=1,
            )
            self.db.add(streak)
        
        self.db.commit()
    
    def get_user_streak(self, user_id: UUID) -> Dict:
        """Get user streak data."""
        streaks = self.db.query(UserStreak).filter(
            UserStreak.user_id == str(user_id)
        ).order_by(UserStreak.date.desc()).all()
        
        if not streaks:
            return {
                "current_streak": 0,
                "longest_streak": 0,
            }
        
        # Calculate current streak (consecutive days from today)
        today = date.today()
        current_streak = 0
        longest_streak = 0
        
        # Calculate longest streak
        if len(streaks) > 0:
            consecutive = 1
            for i in range(len(streaks) - 1):
                if (streaks[i].date - streaks[i + 1].date).days == 1:
                    consecutive += 1
                else:
                    longest_streak = max(longest_streak, consecutive)
                    consecutive = 1
            longest_streak = max(longest_streak, consecutive)
        
        # Calculate current streak from most recent date
        if streaks[0].date == today or streaks[0].date == date.today():
            # Check consecutive days from most recent
            consecutive = 1
            for i in range(len(streaks) - 1):
                if (streaks[i].date - streaks[i + 1].date).days == 1:
                    consecutive += 1
                else:
                    break
            current_streak = consecutive
        
        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
        }
    
    # Property to access game_sessions for statistics (for compatibility)
    @property
    def game_sessions(self):
        """Property to access game sessions (for compatibility with mock_db interface)."""
        sessions = self.db.query(GameSession).all()
        return {
            UUID(session.id): {
                "id": UUID(session.id),
                "user_id": UUID(session.user_id),
                "deck_id": UUID(session.deck_id),
                "word_ids": [UUID(a.word_id) for a in session.game_attempts],
                "score": session.score,
                "started_at": session.started_at,
                "ended_at": session.ended_at,
            }
            for session in sessions
        }


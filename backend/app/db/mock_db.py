"""
Mock database implementation for development.
This will be replaced with a real database (SQLite/PostgreSQL) later.
"""
from datetime import datetime, date
from typing import Optional, List, Dict
from uuid import uuid4, UUID
from app.core.security import get_password_hash


class MockDatabase:
    """In-memory mock database."""
    
    def __init__(self):
        self.users: Dict[UUID, Dict] = {}
        self.decks: Dict[UUID, Dict] = {}
        self.words: Dict[UUID, Dict] = {}
        self.game_sessions: Dict[UUID, Dict] = {}
        self.game_attempts: Dict[UUID, Dict] = {}
        self.student_teacher_associations: List[Dict] = []
        self.user_streaks: Dict[UUID, Dict] = {}
        self._initialize_default_data()
    
    def _initialize_default_data(self):
        """Initialize with default admin user and sample data."""
        # Create default admin user
        # For mock database, use SHA256 hash for faster initialization
        # In production with real database, bcrypt will be used
        admin_id = UUID("00000000-0000-0000-0000-000000000001")
        
        # Use SHA256 for mock database to avoid slow bcrypt initialization
        # The verify_password function will handle both bcrypt and SHA256 hashes
        import hashlib
        password_hash = hashlib.sha256("cantonese".encode()).hexdigest()
        
        self.users[admin_id] = {
            "id": admin_id,
            "username": "admin",
            "password_hash": password_hash,
            "role": "admin",
            "created_at": datetime.utcnow(),
        }
        
        # Create sample deck
        deck_id = UUID("00000000-0000-0000-0000-000000000010")
        self.decks[deck_id] = {
            "id": deck_id,
            "name": "Basic Words",
            "description": "Basic Cantonese words for beginners",
            "created_at": datetime.utcnow(),
        }
        
        # Create sample words
        sample_words = [
            {"text": "你好", "jyutping": "nei5 hou2"},
            {"text": "謝謝", "jyutping": "ze6 ze6"},
            {"text": "再見", "jyutping": "zoi3 gin3"},
            {"text": "早晨", "jyutping": "zou2 san4"},
            {"text": "晚安", "jyutping": "maan5 on1"},
        ]
        
        for word_data in sample_words:
            word_id = uuid4()
            self.words[word_id] = {
                "id": word_id,
                "text": word_data["text"],
                "jyutping": word_data["jyutping"],
                "deck_id": deck_id,
                "created_at": datetime.utcnow(),
            }
    
    # User operations
    def create_user(self, username: str, password: str, role: str) -> Dict:
        """Create a new user."""
        user_id = uuid4()
        try:
            password_hash = get_password_hash(password)
        except Exception:
            # Fallback for bcrypt issues
            import hashlib
            password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        user = {
            "id": user_id,
            "username": username,
            "password_hash": password_hash,
            "role": role,
            "created_at": datetime.utcnow(),
        }
        self.users[user_id] = user
        return user
    
    def get_user_by_id(self, user_id: UUID) -> Optional[Dict]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username."""
        for user in self.users.values():
            if user["username"] == username:
                return user
        return None
    
    # Deck operations
    def create_deck(self, name: str, description: Optional[str] = None) -> Dict:
        """Create a new deck."""
        deck_id = uuid4()
        deck = {
            "id": deck_id,
            "name": name,
            "description": description,
            "created_at": datetime.utcnow(),
        }
        self.decks[deck_id] = deck
        return deck
    
    def get_deck(self, deck_id: UUID) -> Optional[Dict]:
        """Get deck by ID."""
        return self.decks.get(deck_id)
    
    def get_all_decks(self) -> List[Dict]:
        """Get all decks."""
        return list(self.decks.values())
    
    def delete_deck(self, deck_id: UUID) -> bool:
        """Delete a deck."""
        if deck_id in self.decks:
            del self.decks[deck_id]
            # Also delete associated words
            word_ids_to_delete = [
                word_id for word_id, word in self.words.items()
                if word["deck_id"] == deck_id
            ]
            for word_id in word_ids_to_delete:
                del self.words[word_id]
            return True
        return False
    
    # Word operations
    def create_word(self, text: str, jyutping: str, deck_id: UUID) -> Dict:
        """Create a new word."""
        word_id = uuid4()
        word = {
            "id": word_id,
            "text": text,
            "jyutping": jyutping,
            "deck_id": deck_id,
            "created_at": datetime.utcnow(),
        }
        self.words[word_id] = word
        return word
    
    def get_word(self, word_id: UUID) -> Optional[Dict]:
        """Get word by ID."""
        return self.words.get(word_id)
    
    def get_words_by_deck(self, deck_id: UUID) -> List[Dict]:
        """Get all words in a deck."""
        return [word for word in self.words.values() if word["deck_id"] == deck_id]
    
    def delete_word(self, word_id: UUID) -> bool:
        """Delete a word."""
        if word_id in self.words:
            del self.words[word_id]
            return True
        return False
    
    # Game session operations
    def create_game_session(self, user_id: UUID, deck_id: UUID, word_ids: List[UUID]) -> Dict:
        """Create a new game session."""
        session_id = uuid4()
        session = {
            "id": session_id,
            "user_id": user_id,
            "deck_id": deck_id,
            "word_ids": word_ids,
            "score": None,
            "started_at": datetime.utcnow(),
            "ended_at": None,
        }
        self.game_sessions[session_id] = session
        return session
    
    def get_game_session(self, session_id: UUID) -> Optional[Dict]:
        """Get game session by ID."""
        return self.game_sessions.get(session_id)
    
    def update_game_session(self, session_id: UUID, score: Optional[int] = None, ended_at: Optional[datetime] = None):
        """Update game session."""
        if session_id in self.game_sessions:
            if score is not None:
                self.game_sessions[session_id]["score"] = score
            if ended_at is not None:
                self.game_sessions[session_id]["ended_at"] = ended_at
    
    # Game attempt operations
    def create_game_attempt(self, session_id: UUID, word_id: UUID, is_correct: bool, response_time: int) -> Dict:
        """Create a game attempt record."""
        attempt_id = uuid4()
        attempt = {
            "id": attempt_id,
            "session_id": session_id,
            "word_id": word_id,
            "is_correct": is_correct,
            "response_time": response_time,
            "attempted_at": datetime.utcnow(),
        }
        self.game_attempts[attempt_id] = attempt
        return attempt
    
    def get_attempts_by_session(self, session_id: UUID) -> List[Dict]:
        """Get all attempts for a session."""
        return [attempt for attempt in self.game_attempts.values() if attempt["session_id"] == session_id]
    
    def get_attempts_by_user(self, user_id: UUID, deck_id: Optional[UUID] = None) -> List[Dict]:
        """Get all attempts for a user."""
        # Get all sessions for user
        user_sessions = [
            session for session in self.game_sessions.values()
            if session["user_id"] == user_id and (deck_id is None or session["deck_id"] == deck_id)
        ]
        session_ids = [session["id"] for session in user_sessions]
        
        # Get all attempts for those sessions
        attempts = [
            attempt for attempt in self.game_attempts.values()
            if attempt["session_id"] in session_ids
        ]
        return attempts
    
    def get_attempts_by_students(self, student_ids: List[UUID]) -> List[Dict]:
        """Get all attempts for a list of students."""
        user_sessions = [
            session for session in self.game_sessions.values()
            if session["user_id"] in student_ids
        ]
        session_ids = [session["id"] for session in user_sessions]
        
        attempts = [
            attempt for attempt in self.game_attempts.values()
            if attempt["session_id"] in session_ids
        ]
        return attempts
    
    # Student-Teacher association operations
    def create_association(self, student_id: UUID, teacher_id: UUID):
        """Create student-teacher association."""
        # Check if association already exists
        for assoc in self.student_teacher_associations:
            if assoc["student_id"] == student_id and assoc["teacher_id"] == teacher_id:
                return
        
        self.student_teacher_associations.append({
            "student_id": student_id,
            "teacher_id": teacher_id,
            "created_at": datetime.utcnow(),
        })
    
    def get_students_by_teacher(self, teacher_id: UUID) -> List[UUID]:
        """Get all student IDs associated with a teacher."""
        return [
            assoc["student_id"] for assoc in self.student_teacher_associations
            if assoc["teacher_id"] == teacher_id
        ]
    
    def get_all_students(self) -> List[Dict]:
        """Get all students."""
        return [user for user in self.users.values() if user["role"] == "student"]
    
    # User streak operations
    def update_user_streak(self, user_id: UUID, game_date: date):
        """Update user streak for a given date."""
        if user_id not in self.user_streaks:
            self.user_streaks[user_id] = {
                "current_streak": 0,
                "longest_streak": 0,
                "last_game_date": None,
            }
        
        streak_data = self.user_streaks[user_id]
        last_date = streak_data["last_game_date"]
        
        if last_date is None:
            # First game
            streak_data["current_streak"] = 1
            streak_data["longest_streak"] = 1
        elif game_date == last_date:
            # Same day, don't update streak
            pass
        elif (game_date - last_date).days == 1:
            # Consecutive day
            streak_data["current_streak"] += 1
            streak_data["longest_streak"] = max(
                streak_data["longest_streak"],
                streak_data["current_streak"]
            )
        else:
            # Streak broken
            streak_data["current_streak"] = 1
        
        streak_data["last_game_date"] = game_date
    
    def get_user_streak(self, user_id: UUID) -> Dict:
        """Get user streak data."""
        if user_id not in self.user_streaks:
            return {
                "current_streak": 0,
                "longest_streak": 0,
            }
        return {
            "current_streak": self.user_streaks[user_id]["current_streak"],
            "longest_streak": self.user_streaks[user_id]["longest_streak"],
        }
    
    def reset_user_password(self, user_id: UUID, new_password: str) -> bool:
        """Reset user password."""
        if user_id in self.users:
            try:
                password_hash = get_password_hash(new_password)
            except Exception:
                # Fallback for bcrypt issues
                import hashlib
                password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            self.users[user_id]["password_hash"] = password_hash
            return True
        return False


# Global mock database instance (lazy initialization)
_db_instance = None

def get_db():
    """Get or create the global database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = MockDatabase()
    return _db_instance

# Create a simple class to proxy database calls
class DatabaseProxy:
    """Proxy for database operations."""
    def __getattr__(self, name):
        return getattr(get_db(), name)

# Global database proxy
db = DatabaseProxy()


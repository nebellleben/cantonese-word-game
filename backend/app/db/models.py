"""
SQLAlchemy database models.
"""
from datetime import datetime, date
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Date, DateTime, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
import uuid
import enum

from app.db.base import Base


# Use String for UUID to support both SQLite and PostgreSQL
# We'll convert to/from UUID in Python code
def uuid_column():
    """Create a UUID column that works with both SQLite and PostgreSQL."""
    from app.db.base import engine
    if engine.dialect.name == 'postgresql':
        return Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    else:
        return Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))


def uuid_foreign_key(foreign_table):
    """Create a UUID foreign key that works with both SQLite and PostgreSQL."""
    from app.db.base import engine
    if engine.dialect.name == 'postgresql':
        return Column(PostgresUUID(as_uuid=True), ForeignKey(f"{foreign_table}.id"), nullable=False, index=True)
    else:
        return Column(String, ForeignKey(f"{foreign_table}.id"), nullable=False, index=True)


class UserRole(str, enum.Enum):
    """User role enumeration."""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default=UserRole.STUDENT.value)  # Store as string for SQLite compatibility
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    game_sessions = relationship("GameSession", back_populates="user", cascade="all, delete-orphan")
    student_associations = relationship(
        "StudentTeacherAssociation",
        foreign_keys="StudentTeacherAssociation.student_id",
        back_populates="student",
        cascade="all, delete-orphan"
    )
    teacher_associations = relationship(
        "StudentTeacherAssociation",
        foreign_keys="StudentTeacherAssociation.teacher_id",
        back_populates="teacher",
        cascade="all, delete-orphan"
    )
    user_streaks = relationship("UserStreak", back_populates="user", cascade="all, delete-orphan")


class Deck(Base):
    """Deck model."""
    __tablename__ = "decks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    words = relationship("Word", back_populates="deck", cascade="all, delete-orphan")
    game_sessions = relationship("GameSession", back_populates="deck", cascade="all, delete-orphan")


class Word(Base):
    """Word model."""
    __tablename__ = "words"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    text = Column(String, nullable=False)  # Chinese characters
    jyutping = Column(String, nullable=False)  # Jyutping transliteration
    deck_id = Column(String, ForeignKey("decks.id"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    deck = relationship("Deck", back_populates="words")
    game_attempts = relationship("GameAttempt", back_populates="word", cascade="all, delete-orphan")


class GameSession(Base):
    """Game session model."""
    __tablename__ = "game_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    deck_id = Column(String, ForeignKey("decks.id"), nullable=False, index=True)
    score = Column(Integer, nullable=True)  # Calculated when game ends
    started_at = Column(DateTime, nullable=False, server_default=func.now())
    ended_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="game_sessions")
    deck = relationship("Deck", back_populates="game_sessions")
    game_attempts = relationship("GameAttempt", back_populates="session", cascade="all, delete-orphan")


class GameAttempt(Base):
    """Game attempt model - records each pronunciation attempt."""
    __tablename__ = "game_attempts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("game_sessions.id"), nullable=False, index=True)
    word_id = Column(String, ForeignKey("words.id"), nullable=False, index=True)
    is_correct = Column(Boolean, nullable=False)
    response_time = Column(Integer, nullable=False)  # milliseconds
    attempted_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    session = relationship("GameSession", back_populates="game_attempts")
    word = relationship("Word", back_populates="game_attempts")


class StudentTeacherAssociation(Base):
    """Student-Teacher association model."""
    __tablename__ = "student_teacher_associations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    teacher_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    student = relationship("User", foreign_keys=[student_id], back_populates="student_associations")
    teacher = relationship("User", foreign_keys=[teacher_id], back_populates="teacher_associations")
    
    # Unique constraint: prevent duplicate associations
    __table_args__ = (
        UniqueConstraint('student_id', 'teacher_id', name='uq_student_teacher'),
    )


class UserStreak(Base):
    """User streak model - tracks daily game completion for streak calculation."""
    __tablename__ = "user_streaks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    games_completed = Column(Integer, nullable=False, default=1)
    
    # Relationships
    user = relationship("User", back_populates="user_streaks")
    
    # Unique constraint: one record per user per date
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='uq_user_date'),
    )


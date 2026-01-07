from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


# User schemas
class User(BaseModel):
    id: UUID
    username: str
    role: str
    createdAt: datetime = Field(alias="created_at")
    
    model_config = ConfigDict(populate_by_name=True)


# Deck schemas
class Deck(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    createdAt: datetime
    wordCount: int = 0
    
    model_config = ConfigDict(populate_by_name=True)


class CreateDeckRequest(BaseModel):
    name: str
    description: Optional[str] = None


# Word schemas
class Word(BaseModel):
    id: UUID
    text: str
    jyutping: str
    deckId: UUID
    createdAt: datetime
    
    model_config = ConfigDict(populate_by_name=True)


class CreateWordRequest(BaseModel):
    text: str


# Game schemas
class GameWord(BaseModel):
    wordId: UUID
    text: Optional[str] = None
    isCorrect: Optional[bool] = None
    responseTime: Optional[int] = None
    
    model_config = ConfigDict(populate_by_name=True)


class GameSession(BaseModel):
    id: UUID
    userId: UUID
    deckId: UUID
    words: List[GameWord]
    score: Optional[int] = None
    startedAt: datetime
    endedAt: Optional[datetime] = None
    
    model_config = ConfigDict(populate_by_name=True)


class StartGameRequest(BaseModel):
    deckId: UUID
    
    model_config = ConfigDict(populate_by_name=True)


class PronunciationResponse(BaseModel):
    isCorrect: bool
    feedback: Optional[str] = None
    recognizedText: Optional[str] = None
    expectedText: Optional[str] = None
    expectedJyutping: Optional[str] = None
    
    model_config = ConfigDict(populate_by_name=True)


# Statistics schemas
class ScoreByDate(BaseModel):
    date: date
    score: int


class WrongWord(BaseModel):
    wordId: UUID = Field(alias="word_id")
    word: str
    wrongCount: int = Field(alias="wrong_count")
    totalAttempts: int = Field(alias="total_attempts")
    ratio: float
    
    model_config = ConfigDict(populate_by_name=True)


class GameStatistics(BaseModel):
    totalGames: int
    averageScore: float
    bestScore: int
    currentStreak: int
    longestStreak: int
    scoresByDate: List[ScoreByDate]
    topWrongWords: List[WrongWord]
    
    model_config = ConfigDict(populate_by_name=True)


class Student(BaseModel):
    id: UUID
    username: str
    streak: int
    totalScore: int
    
    model_config = ConfigDict(populate_by_name=True)


# Auth schemas
class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str


class AuthResponse(BaseModel):
    token: str
    user: User


# Admin schemas
class AssociationRequest(BaseModel):
    studentId: UUID = Field(alias="student_id")
    teacherId: UUID = Field(alias="teacher_id")
    
    model_config = ConfigDict(populate_by_name=True)


class Association(BaseModel):
    studentId: UUID
    teacherId: UUID


class ResetPasswordRequest(BaseModel):
    password: str


# Error schema
class ErrorResponse(BaseModel):
    error: str
    message: str


from typing import List, Optional
from uuid import UUID
import random
from datetime import datetime, date
from app.db.database_service import DatabaseService
from app.api.models.schemas import GameSession, GameWord, Word
from app.engines.speech_recognition_engine import speech_recognition_engine
import json
import time


DEBUG_LOG_PATH = "/Users/kelvinchan/dev/test/cantonese-word-game/.cursor/debug.log"


class GameService:
    """Service for game operations."""
    
    def __init__(self, db_service: DatabaseService):
        self.db = db_service

    def _log(self, message: str, data: dict, location: str, hypothesis_id: str) -> None:
        """Append a small NDJSON log line for pronunciation debugging."""
        # #region agent log
        try:
            payload = {
                "sessionId": "debug-session",
                "runId": "backend-game",
                "hypothesisId": hypothesis_id,
                "location": location,
                "message": message,
                "data": data,
                "timestamp": int(time.time() * 1000),
            }
            with open(DEBUG_LOG_PATH, "a") as f:
                f.write(json.dumps(payload) + "\n")
        except Exception:
            # Never break game flow on logging failure
            pass
        # #endregion
    
    def start_game(self, user_id: UUID, deck_id: UUID) -> GameSession:
        """Start a new game session."""
        # Verify deck exists
        deck = self.db.get_deck(deck_id)
        if not deck:
            raise ValueError("Deck not found")
        
        # Get all words in deck
        words = self.db.get_words_by_deck(deck_id)
        if not words:
            raise ValueError("Deck has no words")
        
        # Shuffle words (no duplicates)
        word_ids = [word["id"] for word in words]
        random.shuffle(word_ids)
        
        # Create game session
        session = self.db.create_game_session(user_id, deck_id, word_ids)
        
        # Build game words list
        game_words = []
        for word_id in word_ids:
            word = self.db.get_word(word_id)
            game_words.append(GameWord(
                wordId=word_id,
                text=word["text"],
                isCorrect=None,
                responseTime=None
            ))
        
        return GameSession(
            id=session["id"],
            userId=session["user_id"],
            deckId=session["deck_id"],
            words=game_words,
            score=None,
            startedAt=session["started_at"],
            endedAt=None
        )
    
    def submit_pronunciation(
        self,
        session_id: UUID,
        word_id: UUID,
        response_time: int,
        audio_data: bytes = None
    ) -> tuple[bool, str, Optional[str], str, str]:
        """Submit a pronunciation attempt."""
        self._log(
            "submit_pronunciation called",
            {
                "session_id": str(session_id),
                "word_id": str(word_id),
                "response_time": response_time,
                "has_audio": bool(audio_data),
            },
            "game_service.py:submit_pronunciation:1",
            "GAME-A",
        )
        # Verify session exists
        session = self.db.get_game_session(session_id)
        if not session:
            self._log(
                "session not found",
                {"session_id": str(session_id)},
                "game_service.py:submit_pronunciation:2",
                "GAME-B",
            )
            raise ValueError("Game session not found")
        
        # Verify word is in session
        if word_id not in session["word_ids"]:
            self._log(
                "word not in session",
                {"session_id": str(session_id), "word_id": str(word_id), "session_word_ids": [str(w) for w in session["word_ids"]]},
                "game_service.py:submit_pronunciation:3",
                "GAME-C",
            )
            raise ValueError("Word not in this game session")
        
        # Get word data
        word = self.db.get_word(word_id)
        if not word:
            self._log(
                "word not found in DB",
                {"word_id": str(word_id)},
                "game_service.py:submit_pronunciation:4",
                "GAME-D",
            )
            raise ValueError("Word not found")
        
        # Evaluate pronunciation
        is_correct, feedback, recognized_text = speech_recognition_engine.evaluate_pronunciation(
            audio_data or b"",
            word["text"],
            word["jyutping"]
        )
        self._log(
            "pronunciation evaluated",
            {
                "session_id": str(session_id),
                "word_id": str(word_id),
                "is_correct": is_correct,
                "feedback": feedback,
                "recognized_text": recognized_text,
            },
            "game_service.py:submit_pronunciation:5",
            "GAME-E",
        )
        
        # Record attempt
        self.db.create_game_attempt(session_id, word_id, is_correct, response_time)
        
        # Return result with recognized text (Chinese characters) for debugging/comparison
        return is_correct, feedback or "", recognized_text, word["text"], word["jyutping"]
    
    def end_game(self, session_id: UUID) -> GameSession:
        """End a game session and calculate score."""
        session = self.db.get_game_session(session_id)
        if not session:
            raise ValueError("Game session not found")
        
        if session["ended_at"]:
            raise ValueError("Game session already ended")
        
        # Get all attempts for this session
        attempts = self.db.get_attempts_by_session(session_id)
        
        # Calculate score
        correct_count = sum(1 for attempt in attempts if attempt["is_correct"])
        total_words = len(session["word_ids"])
        
        if attempts:
            avg_response_time = sum(attempt["response_time"] for attempt in attempts) / len(attempts)
        else:
            avg_response_time = 0
        
        # Score formula: (correct_words * 100) - (average_response_time / 100)
        score = int((correct_count * 100) - (avg_response_time / 100))
        score = max(0, score)  # Ensure non-negative
        
        # Update session
        ended_at = datetime.utcnow()
        self.db.update_game_session(session_id, score=score, ended_at=ended_at)
        
        # Update user streak if game completed today
        user_id = session["user_id"]
        game_date = date.today()
        self.db.update_user_streak(user_id, game_date)
        
        # Build response with attempt data
        game_words = []
        for word_id in session["word_ids"]:
            word = self.db.get_word(word_id)
            attempt = next(
                (a for a in attempts if a["word_id"] == word_id),
                None
            )
            
            game_words.append(GameWord(
                wordId=word_id,
                text=word["text"],
                isCorrect=attempt["is_correct"] if attempt else None,
                responseTime=attempt["response_time"] if attempt else None
            ))
        
        return GameSession(
            id=session["id"],
            userId=session["user_id"],
            deckId=session["deck_id"],
            words=game_words,
            score=score,
            startedAt=session["started_at"],
            endedAt=ended_at
        )


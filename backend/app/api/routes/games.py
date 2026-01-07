from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from uuid import UUID
from app.api.models.schemas import GameSession, StartGameRequest, PronunciationResponse
from app.core.dependencies import get_current_user, get_db_service
from app.services.game_service import GameService
from app.db.database_service import DatabaseService
import json
import time

DEBUG_LOG_PATH = "/Users/kelvinchan/dev/test/cantonese-word-game/.cursor/debug.log"


def _log(message: str, data: dict, location: str, hypothesis_id: str) -> None:
    """Append a small NDJSON log line for pronunciation route debugging."""
    # #region agent log
    try:
        payload = {
            "sessionId": "debug-session",
            "runId": "backend-games-route",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(time.time() * 1000),
        }
        with open(DEBUG_LOG_PATH, "a") as f:
            f.write(json.dumps(payload) + "\n")
    except Exception:
        # Avoid breaking route on logging failure
        pass
    # #endregion


router = APIRouter(prefix="/games", tags=["Games"])


@router.post("/start", response_model=GameSession, status_code=status.HTTP_201_CREATED)
async def start_game(
    request: StartGameRequest,
    current_user: dict = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Start a new game session."""
    try:
        game_service = GameService(db_service)
        return game_service.start_game(current_user["id"], request.deckId)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/pronunciation", response_model=PronunciationResponse, status_code=status.HTTP_200_OK)
async def submit_pronunciation(
    sessionId: UUID = Form(...),
    wordId: UUID = Form(...),
    responseTime: int = Form(...),
    audio: UploadFile = File(None),
    current_user: dict = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Submit pronunciation attempt."""
    try:
        _log(
            "submit_pronunciation route called",
            {
                "session_id": str(sessionId),
                "word_id": str(wordId),
                "response_time": responseTime,
                "has_current_user": current_user is not None,
            },
            "games.py:submit_pronunciation:1",
            "ROUTE-GAME-A",
        )
        game_service = GameService(db_service)
        audio_data = None
        if audio:
            audio_data = await audio.read()
        
        is_correct, feedback, recognized_text, expected_text, expected_jyutping = game_service.submit_pronunciation(
            sessionId,
            wordId,
            responseTime,
            audio_data
        )
        
        return PronunciationResponse(
            isCorrect=is_correct,
            feedback=feedback,
            recognizedText=recognized_text,
            expectedText=expected_text,
            expectedJyutping=expected_jyutping
        )
    except ValueError as e:
        _log(
            "submit_pronunciation raised ValueError",
            {"error": str(e)},
            "games.py:submit_pronunciation:2",
            "ROUTE-GAME-B",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{session_id}/end", response_model=GameSession, status_code=status.HTTP_200_OK)
async def end_game(
    session_id: UUID,
    current_user: dict = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_db_service)
):
    """End a game session and calculate final score."""
    try:
        game_service = GameService(db_service)
        return game_service.end_game(session_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


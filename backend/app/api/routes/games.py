from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from typing import Optional
from uuid import UUID
from app.api.models.schemas import GameSession, StartGameRequest, PronunciationResponse
from app.core.dependencies import get_current_user, get_db_service
from app.services.game_service import GameService
from app.db.database_service import DatabaseService

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
    realTimeRecognition: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Submit pronunciation attempt."""
    try:
        game_service = GameService(db_service)
        audio_data = None
        if audio:
            audio_data = await audio.read()
        
        is_correct, feedback, recognized_text, expected_text, expected_jyutping = game_service.submit_pronunciation(
            sessionId,
            wordId,
            responseTime,
            audio_data,
            real_time_recognition=realTimeRecognition
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


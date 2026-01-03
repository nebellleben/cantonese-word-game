from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from uuid import UUID
from app.api.models.schemas import GameSession, StartGameRequest, PronunciationResponse
from app.core.dependencies import get_current_user
from app.services.game_service import game_service

router = APIRouter(prefix="/games", tags=["Games"])


@router.post("/start", response_model=GameSession, status_code=status.HTTP_201_CREATED)
async def start_game(
    request: StartGameRequest,
    current_user: dict = Depends(get_current_user)
):
    """Start a new game session."""
    try:
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
    current_user: dict = Depends(get_current_user)
):
    """Submit pronunciation attempt."""
    try:
        audio_data = None
        if audio:
            audio_data = await audio.read()
        
        is_correct, feedback = game_service.submit_pronunciation(
            sessionId,
            wordId,
            responseTime,
            audio_data
        )
        
        return PronunciationResponse(
            isCorrect=is_correct,
            feedback=feedback
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{session_id}/end", response_model=GameSession, status_code=status.HTTP_200_OK)
async def end_game(
    session_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """End a game session and calculate final score."""
    try:
        return game_service.end_game(session_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


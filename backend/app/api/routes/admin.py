from fastapi import APIRouter, HTTPException, status, Depends
from uuid import UUID
from app.api.models.schemas import (
    Deck, Word, CreateDeckRequest, CreateWordRequest,
    AssociationRequest, ResetPasswordRequest
)
from app.core.dependencies import get_current_admin
from app.db.mock_db import db
from app.engines.jyutping_engine import jyutping_engine

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/decks", response_model=Deck, status_code=status.HTTP_201_CREATED)
async def create_deck(
    request: CreateDeckRequest,
    current_user: dict = Depends(get_current_admin)
):
    """Create a new deck."""
    deck = db.create_deck(request.name, request.description)
    return Deck(
        id=deck["id"],
        name=deck["name"],
        description=deck.get("description"),
        createdAt=deck["created_at"]
    )


@router.delete("/decks/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deck(
    deck_id: UUID,
    current_user: dict = Depends(get_current_admin)
):
    """Delete a deck."""
    if not db.delete_deck(deck_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )


@router.post("/decks/{deck_id}/words", response_model=Word, status_code=status.HTTP_201_CREATED)
async def add_word(
    deck_id: UUID,
    request: CreateWordRequest,
    current_user: dict = Depends(get_current_admin)
):
    """Add a word to a deck."""
    deck = db.get_deck(deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    # Generate jyutping
    jyutping = jyutping_engine.get_jyutping(request.text)
    if not jyutping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not generate jyutping for word"
        )
    
    word = db.create_word(request.text, jyutping, deck_id)
    return Word(
        id=word["id"],
        text=word["text"],
        jyutping=word["jyutping"],
        deckId=word["deck_id"],
        createdAt=word["created_at"]
    )


@router.delete("/words/{word_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word(
    word_id: UUID,
    current_user: dict = Depends(get_current_admin)
):
    """Delete a word."""
    if not db.delete_word(word_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )


@router.post("/associations", status_code=status.HTTP_204_NO_CONTENT)
async def create_association(
    request: AssociationRequest,
    current_user: dict = Depends(get_current_admin)
):
    """Associate a student with a teacher."""
    student = db.get_user_by_id(request.studentId)
    teacher = db.get_user_by_id(request.teacherId)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )
    
    if student["role"] != "student":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a student"
        )
    
    if teacher["role"] != "teacher":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a teacher"
        )
    
    db.create_association(request.studentId, request.teacherId)


@router.post("/users/{user_id}/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    user_id: UUID,
    request: ResetPasswordRequest,
    current_user: dict = Depends(get_current_admin)
):
    """Reset password for a user."""
    if not db.reset_user_password(user_id, request.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


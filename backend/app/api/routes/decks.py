from fastapi import APIRouter, HTTPException, status, Depends
from uuid import UUID
from typing import List
from app.api.models.schemas import Deck, Word
from app.core.dependencies import get_current_user, get_db_service
from app.db.database_service import DatabaseService

router = APIRouter(prefix="/decks", tags=["Decks"])


@router.get("", response_model=List[Deck], status_code=status.HTTP_200_OK)
async def get_decks(
    current_user: dict = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get all available decks."""
    decks = db_service.get_all_decks()
    return [
        Deck(
            id=deck["id"],
            name=deck["name"],
            description=deck.get("description"),
            createdAt=deck["created_at"]
        )
        for deck in decks
    ]


@router.get("/{deck_id}/words", response_model=List[Word], status_code=status.HTTP_200_OK)
async def get_words_by_deck(
    deck_id: UUID,
    current_user: dict = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get all words in a deck."""
    deck = db_service.get_deck(deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    words = db_service.get_words_by_deck(deck_id)
    return [
        Word(
            id=word["id"],
            text=word["text"],
            jyutping=word["jyutping"],
            deckId=word["deck_id"],
            createdAt=word["created_at"]
        )
        for word in words
    ]


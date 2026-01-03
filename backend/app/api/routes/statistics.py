from fastapi import APIRouter, HTTPException, status, Depends, Query
from uuid import UUID
from typing import Optional, List
from app.api.models.schemas import GameStatistics, Student, WrongWord
from app.core.dependencies import get_current_user, get_current_teacher_or_admin, get_db_service
from app.services.statistics_service import StatisticsService
from app.db.database_service import DatabaseService

router = APIRouter(prefix="", tags=["Statistics"])


@router.get("/statistics", response_model=GameStatistics, status_code=status.HTTP_200_OK)
async def get_statistics(
    userId: Optional[UUID] = Query(None, alias="userId"),
    deckId: Optional[UUID] = Query(None, alias="deckId"),
    current_user: dict = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get game statistics."""
    statistics_service = StatisticsService(db_service)
    # Check permissions
    target_user_id = userId
    if target_user_id:
        # Only teachers/admins can view other users' stats
        if current_user["role"] not in ["teacher", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other users' statistics"
            )
        
        # Teachers can only view their students' stats
        if current_user["role"] == "teacher":
            student_ids = statistics_service.get_students(current_user["id"], current_user["role"])
            if target_user_id not in [s.id for s in student_ids]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot view this user's statistics"
                )
    
    return statistics_service.get_statistics(
        current_user["id"],
        target_user_id,
        deckId
    )


@router.get("/students", response_model=List[Student], status_code=status.HTTP_200_OK)
async def get_students(
    current_user: dict = Depends(get_current_teacher_or_admin),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get list of students."""
    statistics_service = StatisticsService(db_service)
    return statistics_service.get_students(current_user["id"], current_user["role"])


@router.get("/words/error-ratios", response_model=List[WrongWord], status_code=status.HTTP_200_OK)
async def get_word_error_ratios(
    current_user: dict = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get word error ratios."""
    statistics_service = StatisticsService(db_service)
    return statistics_service.get_word_error_ratios(
        current_user["id"],
        current_user["role"]
    )



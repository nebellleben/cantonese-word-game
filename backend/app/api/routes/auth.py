from fastapi import APIRouter, HTTPException, status, Depends
from app.api.models.schemas import LoginRequest, RegisterRequest, AuthResponse, ErrorResponse
from app.services.auth_service import AuthService
from app.core.dependencies import get_db_service
from app.db.database_service import DatabaseService


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def login(
    request: LoginRequest,
    db_service: DatabaseService = Depends(get_db_service)
):
    """Login user and return JWT token."""
    auth_service = AuthService(db_service)
    user = auth_service.authenticate_user(request.username, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    return auth_service.create_auth_response(user)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db_service: DatabaseService = Depends(get_db_service)
):
    """Register a new user."""
    auth_service = AuthService(db_service)
    try:
        user = auth_service.create_user(
            request.username,
            request.password,
            request.role
        )
        return auth_service.create_auth_response(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )



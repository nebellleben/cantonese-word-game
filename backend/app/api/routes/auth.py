from fastapi import APIRouter, HTTPException, status
from app.api.models.schemas import LoginRequest, RegisterRequest, AuthResponse, ErrorResponse
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def login(request: LoginRequest):
    """Login user and return JWT token."""
    user = auth_service.authenticate_user(request.username, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    return auth_service.create_auth_response(user)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Register a new user."""
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


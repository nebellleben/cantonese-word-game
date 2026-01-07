from typing import Optional
from uuid import UUID
from app.db.database_service import DatabaseService
from app.core.security import verify_password, create_access_token
from app.api.models.schemas import User, AuthResponse
from datetime import timedelta
from app.core.config import settings


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
    
    def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """Authenticate a user and return user data if valid."""
        user = self.db.get_user_by_username(username)
        if not user:
            return None
        
        if not verify_password(password, user["password_hash"]):
            return None
        
        return user
    
    def create_user(self, username: str, password: str, role: str) -> dict:
        """Create a new user."""
        if role not in ["student", "teacher"]:
            raise ValueError("Role must be 'student' or 'teacher'")
        
        return self.db.create_user(username, password, role)
    
    def create_auth_response(self, user: dict) -> AuthResponse:
        """Create an authentication response with token."""
        token_data = {
            "sub": str(user["id"]),
            "username": user["username"],
            "role": user["role"],
        }
        token = create_access_token(token_data)
        
        return AuthResponse(
            token=token,
            user=User(
                id=user["id"],
                username=user["username"],
                role=user["role"],
                created_at=user["created_at"]
            )
        )
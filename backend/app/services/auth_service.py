from typing import Optional
from uuid import UUID
from app.db.mock_db import db
from app.core.security import verify_password, create_access_token
from app.api.models.schemas import User, AuthResponse
from datetime import timedelta
from app.core.config import settings


class AuthService:
    """Service for authentication operations."""
    
    def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """Authenticate a user and return user data if valid."""
        user = db.get_user_by_username(username)
        if not user:
            return None
        
        if not verify_password(password, user["password_hash"]):
            return None
        
        return user
    
    def create_user(self, username: str, password: str, role: str) -> dict:
        """Create a new user."""
        # Check if username already exists
        if db.get_user_by_username(username):
            raise ValueError("Username already exists")
        
        if role not in ["student", "teacher"]:
            raise ValueError("Role must be 'student' or 'teacher'")
        
        return db.create_user(username, password, role)
    
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


auth_service = AuthService()



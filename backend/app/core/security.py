from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
import hashlib


# Configure bcrypt context with explicit backend and SHA-256 fallback
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
try:
    import bcrypt
    pwd_context.load_backend("bcrypt", bcrypt.__name__)
except Exception:
    # Fallback to default backend; verify/get_password_hash will handle errors
    pass


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash (supports bcrypt and legacy SHA-256)."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback for non-bcrypt hashes (for legacy/compat)
        if hashed_password == hashlib.sha256(plain_password.encode()).hexdigest():
            return True
        return False


def get_password_hash(password: str) -> str:
    """Hash a password, with robust fallback if bcrypt backend misbehaves."""
    try:
        # Primary: bcrypt via passlib
        return pwd_context.hash(password)
    except Exception:
        # Fallback: SHA-256 hash (still supported by verify_password)
        return hashlib.sha256(password.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None


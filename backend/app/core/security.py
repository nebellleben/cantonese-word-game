from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Configure bcrypt context with explicit backend to avoid version detection issues
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Force bcrypt backend to avoid version detection issues
try:
    import bcrypt
    pwd_context.load_backend("bcrypt", bcrypt.__name__)
except Exception:
    # Fallback to default
    pass


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback for non-bcrypt hashes (for mock database)
        import hashlib
        if hashed_password == hashlib.sha256(plain_password.encode()).hexdigest():
            return True
        return False


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


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


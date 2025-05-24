from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Secret configuration
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

def _create_token(data: Dict[str, Any], expires_delta: timedelta) -> str:
    """Generate a JWT token with expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(data: Dict[str, Any], expires_minutes: Optional[int] = None) -> str:
    """Create an access token with a default or custom expiration."""
    delta = timedelta(minutes=expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(data, delta)

def create_refresh_token(data: Dict[str, Any], expires_days: Optional[int] = None) -> str:
    """Create a refresh token with a default or custom expiration."""
    delta = timedelta(days=expires_days or REFRESH_TOKEN_EXPIRE_DAYS)
    return _create_token(data, delta)

def verify_token(token: str, secret_key: str = SECRET_KEY, algorithms: list[str] = [ALGORITHM]) -> Optional[Dict[str, Any]]:
    """
    Decode and verify a JWT token. Returns payload or None if invalid.
    """
    try:
        return jwt.decode(token, secret_key, algorithms=algorithms)
    except JWTError:
        return None

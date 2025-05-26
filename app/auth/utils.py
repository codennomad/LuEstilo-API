from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hashes a plain password using bcrypt.
    
    Args:
        password (str): The plain password to be hashed.
        
    Returns:
        str: the hashed password.
    """
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """
    Verifies a plain password against a hashed password.
    
    Args:
        password (str): The plain password input.
        hashed (str): The previously hashed password.
        
    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(password, hashed)

def create_access_token(data: dict, expires_minutes: int = settings.JWT_EXPIRES):
    """
    Creates a JWT access token with an expiration time.
    
    Args:
        data (dict): The data to encode in the token (e.g., User ID or email).
        expires_minutes (int, optional): Token expiration in minutes. Defaults to settings.JWT_EXPIRES.
        
    Returns:
        str: The encoded JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(data: dict, expires_days: int = settings.JWT_REFRESH_EXPIRES):
    """
    Creates a JWT refresh token with a longer expiration time.
    
    Args:
        data(dict): the data to encode in the token.
        expires_days (int, Optional): Token expiration in days. Defaults to settings.JWT_REFRESH_EXPIRES.
        
    Returns:
        str: The encoded JWT refresh token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=expires_days)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str):
    """
    Decodes a JWT token and returns its payload.
    
    Args:
        token (str): str the JWT token to decode.
        
    Returns:
        dict: The payload extracted from the token.
        
    Raises:
        jose.JWTError: if the token is invalid or expired.
    """
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

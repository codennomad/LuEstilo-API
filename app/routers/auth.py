from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_db
from app.schemas.schemas import UserCreate, UserResponse, TokenRefreshRequest, Token
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

auth_service = AuthService()  # Dependência explícita (ou injetável futuramente)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    try:
        return auth_service.register_user(db, user_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    tokens = auth_service.login_user(db, form_data.username, form_data.password)
    if not tokens:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return tokens

@router.post("/refresh-token", response_model=Token)
def refresh_token(payload: TokenRefreshRequest, db: Session = Depends(get_db)):
    token = auth_service.refresh_token(db, payload.username)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid refresh token or user")
    return token

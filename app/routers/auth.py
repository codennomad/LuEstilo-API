from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_db
from app.schemas.schemas import UserCreate, UserResponse, TokenRefreshRequest, Token, TokenWithUser
from app.services.auth import AuthService

router = APIRouter(tags=["auth"])

auth_service = AuthService()  # Dependência explícita (ou injetável futuramente)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, operation_id="register_custom")
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    try:
        return auth_service.register_user(db, user_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=TokenWithUser, operation_id="login_custom")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    tokens = auth_service.login_user(db, form_data.username, form_data.password)
    if not tokens:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return tokens

@router.post("/refresh-token", response_model=Token, operation_id="refresh_token_custom")
def refresh_token(payload: TokenRefreshRequest, db: Session = Depends(get_db)):
    token = auth_service.refresh_token(db, payload.refresh_token)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid refresh token or user")
    return token

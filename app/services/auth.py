# app/services/auth.py
from app.auth.jwt import create_access_token, create_refresh_token,verify_token
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.crud import user as user_crud
from app.schemas.schemas import UserCreate, UserLogin, Token
from app.models.models import User
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "segredo-sombrio")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthService:
    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def authenticate_user(self, db: Session, email: str, password: str) -> User | None:
        user = user_crud.get_user_by_email(db, email)
        if not user or not user_crud.verify_password(password, user.hashed_password):
            return None
        return user

    def register_user(self, db: Session, user_data: UserCreate) -> User:
        existing_user = user_crud.get_user_by_email(db, user_data.email)
        if existing_user:
            raise ValueError("Usuário já existe")
        return user_crud.create_user(db, user_data)
    

    def login_user(self, db: Session, email: str, password: str):
        user = self.authenticate_user(db, email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        new_access_token = create_access_token(data={"sub": str(user.id)}) #data={}
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})#data={}
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role
            }
        }

    def refresh_token(self, db: Session, refresh_token: str):
            payload = verify_token(refresh_token)
            if not payload or "sub" not in payload:
                raise HTTPException(status_code=401, detail="Refresh token inválido ou expirado")
            
            user_id =int(payload["sub"])
            user = user_crud.get_user_by_id(db, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="Usuário não encontrado")
            
            new_access_token = create_access_token(data={"sub": str(user.id)}) #data={}
            new_refresh_token = create_refresh_token(data={"sub": str(user.id)})#data={}
            
            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "role": user.role
                }
            }
        
        

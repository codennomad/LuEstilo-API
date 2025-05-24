from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.user import UserLogin
from app.services import auth as auth_service
from app.database import get_db
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not Found"}},
)

@router.post("/login", summary="Authenticate user and get JWT")
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Realiza o login do usuário.

    - **email**: email cadastrado
    - **password**: senha
    """
    token = auth_service.login_user(db, login_data)
    return JSONResponse(content=token, status_code=status.HTTP_200_OK)

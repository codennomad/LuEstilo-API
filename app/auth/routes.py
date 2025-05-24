from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth import schemas, models, utils, deps

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=schemas.UserResponse)
def register(user_in: schemas.UserCreate, db: Session = Depends(deps.get_db)):
    if db.query(models.User).filter(models.User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    user = models.User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=utils.hash_password(user_in.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=schemas.Token)
def login(user_in: schemas.UserLogin, db: Session = Depends(deps.get_db)):
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if not user or not utils.verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")

    access_token = utils.create_access_token(data={"sub": user.email})
    refresh_token = utils.create_refresh_token(data={"sub": user.email})
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "token_type": "bearer"
        }

@router.post("/refresh-token", response_model=schemas.Token)
def refresh_token(current_user: models.User = Depends(deps.get_current_user)):
    access_token = utils.create_access_token(data={"sub": current_user.email})
    refresh_token = utils.create_refresh_token(data={"sub": current_user.email})
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token,
        "token_type": "bearer"
        }

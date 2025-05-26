from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from datetime import datetime
from app.models.models import User

#Criar um usuário (entrada)
#class UserCreate(BaseModel):
    #name: str
    #email: EmailStr
    #password: str
    #role: Optional[Literal["admin", "user"]] = 
    
#login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

#Retorno de usuário (sem senha)
class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    is_admin: User.is_admin
    created_at: datetime

    class Config:
        from_attributes = True

#Retorna o JWT (fazer login)
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
   
#Decodificar e validar o sub(email)
class TokenData(BaseModel):
    email: Optional[EmailStr] = None

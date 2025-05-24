from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, EmailStr
from enum import Enum


# ENUMS

class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    USER = "user"


# USER SCHEMAS

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRoleEnum

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRoleEnum] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# CLIENT SCHEMAS

class ClientBase(BaseModel):
    name: str
    email: EmailStr
    cpf: str

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf: Optional[str] = None

class ClientResponse(ClientBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# PRODUCT SCHEMAS

class ProductBase(BaseModel):
    description: str
    price: float  # Se for Decimal no model, melhor usar condecimal aqui
    barcode: str
    section: str
    stock: int
    expiry_date: Optional[date] = None
    images: Optional[List[str]] = None  # Se armazenar JSON ou lista de caminhos

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    description: Optional[str] = None
    price: Optional[float] = None
    barcode: Optional[str] = None
    section: Optional[str] = None
    stock: Optional[int] = None
    expiry_date: Optional[date] = None
    images: Optional[List[str]] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ORDER SCHEMAS

class OrderBase(BaseModel):
    client_id: int
    status: str

class OrderCreate(OrderBase):
    product_ids: List[int]

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    product_ids: Optional[List[int]] = None

class OrderResponse(OrderBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    products: List[ProductResponse]
    client: ClientResponse

    class Config:
        from_attributes = True


# AUTH SCHEMAS

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: Optional[str] = None  # usually user email

class TokenRefreshRequest(BaseModel):
    username: str

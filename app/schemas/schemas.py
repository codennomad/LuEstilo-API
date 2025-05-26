from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, field_validator
from app.models.models import UserRole as UserRoleEnum
from enum import Enum
from decimal import Decimal
import json


# USER SCHEMAS

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRoleEnum

class UserCreate(UserBase): # add
    name: str #
    email: EmailStr #
    password: str
    role: UserRoleEnum #

class UserUpdate(BaseModel):
    name: Optional[str] = None
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
    
    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, v):
        if not v.isdigit() or len(v) != 11:
            raise ValueError("CPF must contain 11 numeric digits")
        return v

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
    price: Decimal
    barcode: str
    section: str
    stock: int
    expiry_date: Optional[date] = None
    images: Optional[List[str]] = None  # Se armazenar JSON ou lista de caminhos

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    description: Optional[str] = None
    price: Optional[Decimal] = None
    barcode: Optional[str] = None
    section: Optional[str] = None
    stock: Optional[int] = None
    expiry_date: Optional[date] = None
    images: Optional[List[str]] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_validator("images", mode="before")
    @classmethod
    def parse_images(cls, v):
        if isinstance(v, str):
            try:
                data = json.loads(v)
                if isinstance(data, list) and all(isinstance(i, str) for i in data):
                    return data
            except json.JSONDecodeError:
                pass
            return[]
        return v

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: str(v)
        }


# ORDER SCHEMAS

class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderBase(BaseModel):
    client_id: int
    status: OrderStatusEnum

class OrderCreate(OrderBase):
    client_id: int
    status: str
    product_ids: List[int]

class OrderUpdate(BaseModel):
    status: Optional[OrderStatusEnum] = None
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
    refresh_token: str
    token_type: str 
    user: dict

class TokenData(BaseModel):
    sub: Optional[str] = None  # usually user email

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class UserInToken(BaseModel):
    id: int
    email: str
    name: str
    role: UserRoleEnum
    
class TokenWithUser(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserInToken
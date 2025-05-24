from sqlalchemy import (
    Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Table, Text, Enum, Boolean
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum
from decimal import Decimal

Base = declarative_base()

class UserRole(enum.Enum):
    """
    Enumeration for user roles.
    """
    ADMIN = "admin"
    USER = "user"

# Association table for many-to-many relationship between Order and Product
order_product = Table(
    "order_product",
    Base.metadata,
    Column("order_id", Integer, ForeignKey("orders.id"), primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True)
)

class User(Base):
    """
    User model representing system users with authentication and role-based access.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    hashed_password = Column(String(128), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def is_admin(self) -> bool:
        """
        Check if the user has administrative privileges.
        
        Returns:
            bool: True if user is an admin, False otherwise.
        """
        return self.role == UserRole.ADMIN

class Client(Base):
    """
    Client model representing customers who place orders.
    """
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    cpf = Column(String(14), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    orders = relationship("Order", back_populates="client")

class Product(Base):
    """
    Product model representing items available for sale.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(255), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)  # Using Numeric for precision
    barcode = Column(String(64), unique=True, nullable=False, index=True)
    section = Column(String(64), nullable=False)
    stock = Column(Integer, nullable=False)
    expiry_date = Column(Date, nullable=True)
    images = Column(Text, nullable=True)  # Can store JSON string or file paths
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    orders = relationship(
        "Order",
        secondary=order_product,
        back_populates="products"
    )

class Order(Base):
    """
    Order model representing purchase transactions made by clients.
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    status = Column(String(32), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    client = relationship("Client", back_populates="orders")
    products = relationship(
        "Product",
        secondary=order_product,
        back_populates="orders"
    )

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from decimal import Decimal

from app.database import get_db
from app.models.models import Product
from app.schemas.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.auth.deps import get_current_user, require_admin, require_user

import json

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[ProductResponse])
def list_products(
    db: Session = Depends(get_db),
    current_user = Depends(require_user),
    section: Optional[str] = Query(None, description="Filter by section/category"),
    min_price: Optional[Decimal] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[Decimal] = Query(None, ge=0, description="Maximum price"),
    available: Optional[bool] = Query(None, description="Only available products (stock > 0)"),
    skip: int = Query(0, ge=0, description="Number of record to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max records to return"),
    ):
    """
    Retrieve a list of products with optional filters and pagination.
    
    -section: Product category
    -min_price: Minimum price
    -max_price: Maximum price
    -available: Only products in stock
    -skip: Records to skip
    -limit: Max records to return
    """
    query = db.query(Product)
    if section:
        query = query.filter(Product.section == section)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if available:
        query = query.filter(Product.stock > 0)
    products = query.offset(skip).limit(limit).all()
    return products

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product_in: ProductCreate, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    """
    Create a new product.
    
    Required fields:
    -description
    -price
    -barcode
    -section
    -stock
    
    Opional fields:
    -expiry_date
    -images
    """
    if db.query(Product).filter(Product.barcode == product_in.barcode).first():
        raise HTTPException(status_code=400, detail="Barcode already registered")
    
    images = json.dumps(product_in.images) if product_in.images else None
        
    product = Product(
        description=product_in.description,
        price=product_in.description,
        barcode=product_in.barcode,
        section=product_in.section,
        stock=product_in.stock,
        expiry_date=product_in.expiry_date,
        images=images
    )
    db.add(product)
    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Barcode already registered")
    return product

@router.get("/{id}", response_model=ProductResponse)
def get_product(id: int, db: Session = Depends(get_db), current_user = Depends(require_user)):
    """Retrieve product details by ID"""
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{id}", response_model=ProductResponse)
def update_product(id: int, product_in: ProductUpdate, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    """
    Update an existing product by ID
    
    -Checks for barcode duplication
    -Updates only provided fields
    """
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product_in.barcode and product_in.barcode != product.barcode:
        if db.query(Product).filter(Product.barcode == product_in.barcode).first():
            raise HTTPException(status_code=400, detail="Barcode already registered")
        product.barcode = product_in.barcode
    if product_in.description is not None:
        product.description = product_in.description
    if product_in.price is not None:
        product.price = product_in.price
    if product_in.section is not None:
        product.section = product_in.section
    if product_in.stock is not None:
        product.stock = product_in.stock
    if product_in.expiry_date is not None:
        product.expiry_date = product_in.expiry_date
    if product_in.images is not None:
        product.images = json.dumps(product_in.images)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(id: int, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    """Delete a product by ID"""
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return None

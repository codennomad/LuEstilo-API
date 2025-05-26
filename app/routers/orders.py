from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime, date

from app.database import get_db
from app.models.models import Order, Product, Client
from app.schemas.schemas import OrderCreate, OrderUpdate, OrderResponse
from app.auth.deps import require_user, require_admin

router = APIRouter(tags=["orders"])

@router.get(
    "/",
    response_model=List[OrderResponse],
    summary="List orders",
    description="Retrieve a list of orders with optional filter for date range, section, order ID, status, and client.",
    response_description= "A list of orders matching the filters."
)
def list_orders(
    db: Session = Depends(get_db),
    current_user = Depends(require_user),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    section: Optional[str] = Query(None, description="Product section"),
    order_id: Optional[int] = Query(None, description="Order ID"),
    status: Optional[str] = Query(None, description="Order status"),
    client_id: Optional[int] = Query(None, description="Client ID"),
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max records to return"),
 ):
    """
    Retrieve a list of orders from the database with optional filters.
    
    Args:
        db (Session): SQLAlchemy database session.
        start_date (Optional[date]): Filter by start date.
        end_date (Optional[str]): Filter by end date.
        section (Optional[str]): Filter by product section.
        order_id (Optional[int]): Filter by specific order ID.
        status (Optional[str]): Filter by order status.
        client_id (Optional[int]): Filter by client ID.
        skip (int): Number of records to skip.
        limit(int): Maximum number of records to return.
        
    Returns:
        List[OrderResponse]: A list of orders matching the filters.
    """
    query = db.query(Order).options(
        joinedload(Order.products),
        joinedload(Order.client)
    )
    if order_id:
        query = query.filter(Order.id == order_id)
    if status:
        query = query.filter(Order.status == status)
    if client_id:
        query = query.filter(Order.client_id == client_id)
    if start_date:
        query = query.filter(Order.created_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(Order.created_at <= datetime.combine(end_date, datetime.max.time()))
    if section:
        query = query.join(Order.products).filter(Product.section == section)
    return query.offset(skip).limit(limit).all()

@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Order",
    description="Create a new order for a client with one or more products. Validates stock availability.",
    response_description="The created order.",
)
def create_order(order_in: OrderCreate, db: Session = Depends(get_db), current_user= Depends(require_admin)):
    """
    Create a new order with associated products and client.
    
    Args:
        order_ir (OrderCreate): Input data for the new order.
        db(session): SQLAlchemy database session.
        
    Raises:
        HTTPException: if the client or any products is not found, or if stock is insufficient.
        
    Returns:
        OrderResponse: The newly created order.
    """
    client = db.query(Client).filter(Client.id == order_in.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    products = db.query(Product).filter(Product.id.in_(order_in.product_ids)).with_for_update().all()
    if len(products) != len(order_in.product_ids):
        raise HTTPException(status_code=404, detail="One or more products not found")
    
    insufficient = [p.id for p in products if p.stock < 1]
    if insufficient:
        raise HTTPException(status_code=400, detail=f"Insufficient stock for products: {insufficient}")
    
    for p in products:
        p.stock -=1
        
    order = Order(
        client_id=order_in.client_id,
        status=order_in.status,
        products=products
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

@router.get(
    "/{id}",
    response_model=OrderResponse,
    summary="Get order by ID",
    description="Retrieve a specific order by its ID.",
    response_description="The order with the specified ID."
)
def get_order(id: int, db: Session = Depends(get_db), current_user= Depends(require_user)):
    """
    Retrieve a specific order by its ID.
    
    Args:
        id (int): ID of the order.
        db(Session): SQLAlchemy database session.
        
    Raises:
        HTTPException: if the order is not found.
        
    Returns:
        OrderResponse: The order data.
    """
    order = db.query(Order).options(
        joinedload(Order.products),
        joinedload(Order.client)
    ).filter(Order.id == id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order

@router.put(
    "/{id}",
    response_model=OrderResponse,
    summary="Update order status or products",
    description="Update the status of an order and/or its products.",
    response_description="The update order."
)
def update_order(id: int, order_in: OrderUpdate, db: Session = Depends(get_db), current_user= Depends(require_admin)):
    """
    Update the status or products of an existing order.
    
    Args:
        id(int): ID of the order.
        order_in (OrderUpdate): Updated order data.
        db (Session): SQLAlchemy database session.
        
    Raises:
        HTTPException: if the order or any of the specifies products are not found.
        
    Returns:
        OrderResponse: The updated order.
    """
    order = db.query(Order).options(joinedload(Order.products)).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order_in.status is not None:
        order.status = order_in.status
        
    if order_in.product_ids is not None:
        products = db.query(Product).filter(Product.id.in_(order_in.product_ids)).all()
        if len (products) != len(order_in.product_ids):
            raise HTTPException(status_code=404, detail="One or more products not found")
        order.products = products
        
    db.commit()
    db.refresh(order)
    return order

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete order",
    description="Delete an order by its ID.",
    response_description="No content."
)
def delete_order(id: int, db: Session = Depends(get_db), current_user= Depends(require_admin)):
    """
    Delete an order by its ID.
    
    Args:
        id (int): ID of the order to delete.
        db (session): SQLAlchemy database session.
        
    Raises:
        HTTPException: if the order is not found.
        
    Returns:
        None
    """
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db.delete(order)
    db.commit()
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from app.database import get_db
from app.models.models import Client
from app.schemas.schemas import ClientCreate, ClientUpdate, ClientResponse
from app.auth.deps import get_current_user, require_admin

router = APIRouter(tags=["clients"])

@router.get("/", response_model=List[ClientResponse])
def list_clients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    name: Optional[str] = Query(None, description="Filter by client name"),
    email: Optional[str] = Query(None, description="Filter by client email"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve a list of clients with optional filters by name and email.
    Suports pagination using skip and limit.
    """
    query = db.query(Client)
    if name:
        query = query.filter(Client.name.ilike(f"%{name}%"))
    if email:
        query = query.filter(Client.email.ilike(f"%{email}%"))
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    client_in: ClientCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Create a new client.
    Ensures email and CPF are unique.
    Requires admin privileges
    """
    if db.query(Client).filter(Client.email == client_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(Client).filter(Client.cpf == client_in.cpf).first():
        raise HTTPException(status_code=400, detail="CPF already registered")
    
    client = Client(name=client_in.name, email=client_in.email, cpf=client_in.cpf)
    db.add(client)
    try:
        db.commit()
        db.refresh(client)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email or CPF already registered")
    return client

@router.get("/{id}", response_model=ClientResponse)
def get_client(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    retrieve a specific client's information by ID.
    """
    client = db.query(Client).filter(Client.id == id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.put("/{id}", response_model=ClientResponse)
def update_client(
    id: int,
    client_in: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Update an existing client's information by ID.
    Validates unique email and CPF if update.
    Requires admin privileges.
    """
    client = db.query(Client).filter(Client.id == id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    if client_in.email and client_in.email != client.email:
        if db.query(Client).filter(Client.email == client_in.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        client.email = client_in.email
        
    if client_in.cpf and client_in.cpf != client.cpf:
        if db.query(Client).filter(client.cpf == client_in.cpf).first():
            raise HTTPException(status_code=400, detail="CPF already registered")
        client.cpf = client_in.cpf
        
    if client_in.name is not None:
        client.name = client_in.name
        
    db.commit()
    db.refresh(client)
    return client

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_clint(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Delete a specific client by ID.
    Requires admin privileges.
    """
    client = db.query(Client).filter(Client.id == id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(client)
    db.commit()
    return None
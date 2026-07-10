from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app import crud, schemas
from app.database import get_db
from app.utils.validators import validate_email, validate_phone
import secrets

router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.post("/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    # Validate customer info
    if not validate_email(order.customer_email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    if not validate_phone(order.customer_phone):
        raise HTTPException(status_code=400, detail="Invalid phone number")
    
    # Generate order number
    order_number = f"ORD-{secrets.token_hex(8).upper()}"
    
    # Create order with order number
    order_data = order.dict()
    order_data['order_number'] = order_number
    order_create = schemas.OrderCreate(**order_data)
    
    return crud.create_order(db, order_create)

@router.get("/", response_model=List[schemas.Order])
def read_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return crud.get_orders(db, skip=skip, limit=limit, status=status)

@router.get("/{order_id}", response_model=schemas.Order)
def read_order(order_id: int, db: Session = Depends(get_db)):
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/{order_id}", response_model=schemas.Order)
def update_order(
    order_id: int,
    order_update: schemas.OrderUpdate,
    db: Session = Depends(get_db)
):
    db_order = crud.get_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return crud.update_order(db, order_id, order_update)

@router.delete("/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    crud.delete_order(db, order_id)
    return {"message": "Order deleted successfully"}
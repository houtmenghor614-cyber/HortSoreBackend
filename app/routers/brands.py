from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/api/brands", tags=["brands"])

@router.post("/", response_model=schemas.Brand, status_code=status.HTTP_201_CREATED)
def create_brand(
    brand: schemas.BrandCreate,
    db: Session = Depends(get_db)
):
    return crud.create_brand(db, brand)

@router.get("/", response_model=List[schemas.Brand])
def read_brands(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    brands = crud.get_brands(db, skip=skip, limit=limit)
    return brands

@router.get("/{brand_id}", response_model=schemas.Brand)
def read_brand(
    brand_id: int,
    db: Session = Depends(get_db)
):
    brand = crud.get_brand(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand

@router.put("/{brand_id}", response_model=schemas.Brand)
def update_brand(
    brand_id: int,
    brand: schemas.BrandUpdate,
    db: Session = Depends(get_db)
):
    db_brand = crud.get_brand(db, brand_id)
    if not db_brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return crud.update_brand(db, brand_id, brand)

@router.delete("/{brand_id}")
def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db)
):
    brand = crud.get_brand(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    crud.delete_brand(db, brand_id)
    return {"message": "Brand deleted successfully"}
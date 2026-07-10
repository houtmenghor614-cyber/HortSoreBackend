from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app import crud, schemas
from app.database import get_db
from app.utils.file_upload import file_upload

router = APIRouter(prefix="/api/banners", tags=["banners"])

@router.post("/", response_model=schemas.Banner)
async def create_banner(
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    link_url: Optional[str] = Form(None),
    order_position: int = Form(0),
    is_active: bool = Form(True),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Save image
    image_path = await file_upload.save_file(image, "banners")
    
    banner_data = schemas.BannerCreate(
        title=title,
        description=description,
        link_url=link_url,
        order_position=order_position,
        is_active=is_active
    )
    
    return crud.create_banner(db, banner_data, image_path)

@router.get("/", response_model=List[schemas.Banner])
def read_banners(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    return crud.get_banners(db, skip=skip, limit=limit, is_active=is_active)

@router.get("/{banner_id}", response_model=schemas.Banner)
def read_banner(banner_id: int, db: Session = Depends(get_db)):
    banner = crud.get_banner(db, banner_id)
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    return banner

@router.put("/{banner_id}", response_model=schemas.Banner)
async def update_banner(
    banner_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    link_url: Optional[str] = Form(None),
    order_position: Optional[int] = Form(None),
    is_active: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    banner = crud.get_banner(db, banner_id)
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    
    update_data = schemas.BannerUpdate(
        title=title,
        description=description,
        link_url=link_url,
        order_position=order_position,
        is_active=is_active
    )
    
    # Update image if provided
    if image:
        # Delete old image
        if banner.image_path:
            file_upload.delete_file(banner.image_path)
        image_path = await file_upload.save_file(image, "banners")
        banner = crud.update_banner(db, banner_id, update_data, image_path)
    else:
        banner = crud.update_banner(db, banner_id, update_data)
    
    return banner

@router.delete("/{banner_id}")
def delete_banner(banner_id: int, db: Session = Depends(get_db)):
    banner = crud.get_banner(db, banner_id)
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    
    # Delete image
    if banner.image_path:
        file_upload.delete_file(banner.image_path)
    
    crud.delete_banner(db, banner_id)
    return {"message": "Banner deleted successfully"}
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app import crud, schemas
from app.database import get_db
from app.utils.file_upload import file_upload
import json

router = APIRouter(prefix="/api/products", tags=["products"])

@router.post("/", response_model=schemas.Product)
async def create_product(
    title: str = Form(...),
    original_price: float = Form(...),
    discount_price: Optional[float] = Form(None),
    description: Optional[str] = Form(None),
    category_id: int = Form(...),
    stock_quantity: int = Form(0),
    is_active: bool = Form(True),
    colors: Optional[str] = Form('[]'),
    sizes: Optional[str] = Form('[]'),
    main_image: Optional[UploadFile] = File(None),
    sub_images: List[UploadFile] = File([]),
    db: Session = Depends(get_db)
):
    try:
        # Parse colors and sizes
        colors_list = json.loads(colors) if colors else []
        sizes_list = json.loads(sizes) if sizes else []
        
        # Create product data
        product_data = schemas.ProductCreate(
            title=title,
            original_price=original_price,
            discount_price=discount_price,
            description=description,
            category_id=category_id,
            stock_quantity=stock_quantity,
            is_active=is_active,
            colors=[schemas.ProductColorCreate(**c) for c in colors_list],
            sizes=[schemas.ProductSizeCreate(**s) for s in sizes_list],
            sub_images=[]
        )
        
        # Create product
        product = crud.create_product(db, product_data)
        
        # Save main image
        if main_image:
            main_path = await file_upload.save_file(main_image, "products/main")
            product = crud.update_product_main_image(db, product.id, main_path)
        
        # Save sub images
        if sub_images:
            for img in sub_images:
                if img and img.filename:
                    sub_path = await file_upload.save_file(img, "products/sub")
                    crud.create_product_sub_image(db, product.id, sub_path, False)
        
        return product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[schemas.Product])
def read_products(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return crud.get_products(db, skip=skip, limit=limit, category_id=category_id, search=search)

@router.get("/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=schemas.Product)
async def update_product(
    product_id: int,
    title: Optional[str] = Form(None),
    original_price: Optional[float] = Form(None),
    discount_price: Optional[float] = Form(None),
    description: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    stock_quantity: Optional[int] = Form(None),
    is_active: Optional[bool] = Form(None),
    colors: Optional[str] = Form(None),
    sizes: Optional[str] = Form(None),
    main_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update basic info
    update_data = schemas.ProductUpdate(
        title=title,
        original_price=original_price,
        discount_price=discount_price,
        description=description,
        category_id=category_id,
        stock_quantity=stock_quantity,
        is_active=is_active
    )
    
    product = crud.update_product(db, product_id, update_data)
    
    # Update colors if provided
    if colors:
        colors_list = json.loads(colors)
        crud.update_product_colors(db, product_id, colors_list)
    
    # Update sizes if provided
    if sizes:
        sizes_list = json.loads(sizes)
        crud.update_product_sizes(db, product_id, sizes_list)
    
    # Update main image if provided
    if main_image:
        # Delete old image
        if product.main_image:
            file_upload.delete_file(product.main_image)
        main_path = await file_upload.save_file(main_image, "products/main")
        product = crud.update_product_main_image(db, product_id, main_path)
    
    return product

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Delete all associated images
    if product.main_image:
        file_upload.delete_file(product.main_image)
    for sub_img in product.sub_images:
        file_upload.delete_file(sub_img.image_path)
    
    crud.delete_product(db, product_id)
    return {"message": "Product deleted successfully"}

@router.post("/{product_id}/sub-images")
async def add_sub_images(
    product_id: int,
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    saved_paths = []
    for img in images:
        if img and img.filename:
            path = await file_upload.save_file(img, "products/sub")
            crud.create_product_sub_image(db, product_id, path, False)
            saved_paths.append(path)
    
    return {"message": f"Added {len(saved_paths)} images", "paths": saved_paths}

@router.delete("/sub-images/{image_id}")
def delete_sub_image(image_id: int, db: Session = Depends(get_db)):
    sub_image = crud.delete_product_sub_image(db, image_id)
    if not sub_image:
        raise HTTPException(status_code=404, detail="Image not found")
    file_upload.delete_file(sub_image.image_path)
    return {"message": "Image deleted successfully"}
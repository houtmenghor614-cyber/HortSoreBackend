from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from app import models, schemas

# ==================== CATEGORY CRUD ====================
def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).offset(skip).limit(limit).all()

def get_category(db: Session, category_id: int):
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def update_category(db: Session, category_id: int, category: schemas.CategoryCreate):
    db_category = get_category(db, category_id)
    if db_category:
        for key, value in category.dict().items():
            setattr(db_category, key, value)
        db.commit()
        db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int):
    db_category = get_category(db, category_id)
    if db_category:
        db.delete(db_category)
        db.commit()
    return db_category

# ==================== BRAND CRUD ====================
def create_brand(db: Session, brand: schemas.BrandCreate):
    db_brand = models.Brand(**brand.dict())
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand

def get_brands(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Brand).offset(skip).limit(limit).all()

def get_brand(db: Session, brand_id: int):
    return db.query(models.Brand).filter(models.Brand.id == brand_id).first()

def update_brand(db: Session, brand_id: int, brand: schemas.BrandUpdate):
    db_brand = get_brand(db, brand_id)
    if db_brand:
        update_data = brand.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_brand, key, value)
        db.commit()
        db.refresh(db_brand)
    return db_brand

def delete_brand(db: Session, brand_id: int):
    db_brand = get_brand(db, brand_id)
    if db_brand:
        db.delete(db_brand)
        db.commit()
    return db_brand

# ==================== PRODUCT CRUD ====================
def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(
        title=product.title,
        original_price=product.original_price,
        discount_price=product.discount_price,
        description=product.description,
        category_id=product.category_id,
        stock_quantity=product.stock_quantity,
        is_active=product.is_active
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Add colors
    for color in product.colors:
        db_color = models.ProductColor(
            product_id=db_product.id,
            color_name=color.color_name,
            color_code=color.color_code
        )
        db.add(db_color)
    
    # Add sizes
    for size in product.sizes:
        db_size = models.ProductSize(
            product_id=db_product.id,
            size_name=size.size_name,
            stock_quantity=size.stock_quantity
        )
        db.add(db_size)
    
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products(db: Session, skip: int = 0, limit: int = 100, category_id: Optional[int] = None, search: Optional[str] = None):
    query = db.query(models.Product)
    
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    
    if search:
        query = query.filter(
            or_(
                models.Product.title.contains(search),
                models.Product.description.contains(search)
            )
        )
    
    return query.filter(models.Product.is_active == True).offset(skip).limit(limit).all()

def get_all_products(db: Session, skip: int = 0, limit: int = 100):
    """Get all products including inactive ones (for admin)"""
    return db.query(models.Product).offset(skip).limit(limit).all()

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def update_product(db: Session, product_id: int, product: schemas.ProductUpdate):
    db_product = get_product(db, product_id)
    if db_product:
        update_data = product.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product

def update_product_main_image(db: Session, product_id: int, image_path: str):
    db_product = get_product(db, product_id)
    if db_product:
        db_product.main_image = image_path
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = get_product(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product

def update_product_colors(db: Session, product_id: int, colors: List[dict]):
    db.query(models.ProductColor).filter(models.ProductColor.product_id == product_id).delete()
    
    for color in colors:
        db_color = models.ProductColor(
            product_id=product_id,
            color_name=color.get('color_name'),
            color_code=color.get('color_code')
        )
        db.add(db_color)
    
    db.commit()
    return True

def update_product_sizes(db: Session, product_id: int, sizes: List[dict]):
    db.query(models.ProductSize).filter(models.ProductSize.product_id == product_id).delete()
    
    for size in sizes:
        db_size = models.ProductSize(
            product_id=product_id,
            size_name=size.get('size_name'),
            stock_quantity=size.get('stock_quantity', 0)
        )
        db.add(db_size)
    
    db.commit()
    return True

def create_product_sub_image(db: Session, product_id: int, image_path: str, is_primary: bool = False):
    db_sub_image = models.ProductSubImage(
        product_id=product_id,
        image_path=image_path,
        is_primary=is_primary
    )
    db.add(db_sub_image)
    db.commit()
    db.refresh(db_sub_image)
    return db_sub_image

def delete_product_sub_image(db: Session, image_id: int):
    db_sub_image = db.query(models.ProductSubImage).filter(models.ProductSubImage.id == image_id).first()
    if db_sub_image:
        db.delete(db_sub_image)
        db.commit()
    return db_sub_image

# ==================== BANNER CRUD ====================
def create_banner(db: Session, banner: schemas.BannerCreate, image_path: str):
    db_banner = models.Banner(
        title=banner.title,
        description=banner.description,
        link_url=banner.link_url,
        order_position=banner.order_position,
        is_active=banner.is_active,
        image_path=image_path
    )
    db.add(db_banner)
    db.commit()
    db.refresh(db_banner)
    return db_banner

def get_banners(db: Session, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None):
    query = db.query(models.Banner)
    if is_active is not None:
        query = query.filter(models.Banner.is_active == is_active)
    return query.order_by(models.Banner.order_position).offset(skip).limit(limit).all()

def get_banner(db: Session, banner_id: int):
    return db.query(models.Banner).filter(models.Banner.id == banner_id).first()

def update_banner(db: Session, banner_id: int, banner: schemas.BannerUpdate, image_path: Optional[str] = None):
    db_banner = get_banner(db, banner_id)
    if db_banner:
        update_data = banner.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_banner, key, value)
        if image_path:
            db_banner.image_path = image_path
        db.commit()
        db.refresh(db_banner)
    return db_banner

def delete_banner(db: Session, banner_id: int):
    db_banner = get_banner(db, banner_id)
    if db_banner:
        db.delete(db_banner)
        db.commit()
    return db_banner

# ==================== ORDER CRUD ====================
def create_order(db: Session, order: schemas.OrderCreate):
    total = sum(item.price * item.quantity for item in order.items)
    
    db_order = models.Order(
        order_number=order.order_number,
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        customer_phone=order.customer_phone,
        shipping_address=order.shipping_address,
        total_amount=total,
        payment_method=order.payment_method,
        status="pending",
        payment_status="unpaid"
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    for item in order.items:
        db_item = models.OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            product_name=item.product_name,
            color=item.color,
            size=item.size,
            quantity=item.quantity,
            price=item.price
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None):
    query = db.query(models.Order)
    if status:
        query = query.filter(models.Order.status == status)
    return query.order_by(models.Order.created_at.desc()).offset(skip).limit(limit).all()

def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def update_order(db: Session, order_id: int, order: schemas.OrderUpdate):
    db_order = get_order(db, order_id)
    if db_order:
        update_data = order.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_order, key, value)
        db.commit()
        db.refresh(db_order)
    return db_order

def delete_order(db: Session, order_id: int):
    db_order = get_order(db, order_id)
    if db_order:
        db.delete(db_order)
        db.commit()
    return db_order
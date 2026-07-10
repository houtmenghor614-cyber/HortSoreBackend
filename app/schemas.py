from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ==================== CATEGORY SCHEMAS ====================
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== BRAND SCHEMAS ====================
class BrandBase(BaseModel):
    name: str
    description: Optional[str] = None
    logo: Optional[str] = None

class BrandCreate(BrandBase):
    pass

class BrandUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None

class Brand(BrandBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== PRODUCT COLOR SCHEMAS ====================
class ProductColorBase(BaseModel):
    color_name: str
    color_code: Optional[str] = None

class ProductColorCreate(ProductColorBase):
    pass

class ProductColor(ProductColorBase):
    id: int
    product_id: int

    class Config:
        from_attributes = True

# ==================== PRODUCT SIZE SCHEMAS ====================
class ProductSizeBase(BaseModel):
    size_name: str
    stock_quantity: int = 0

class ProductSizeCreate(ProductSizeBase):
    pass

class ProductSize(ProductSizeBase):
    id: int
    product_id: int

    class Config:
        from_attributes = True

# ==================== PRODUCT SUB IMAGE SCHEMAS ====================
class ProductSubImageBase(BaseModel):
    image_path: str
    is_primary: bool = False

class ProductSubImageCreate(ProductSubImageBase):
    pass

class ProductSubImage(ProductSubImageBase):
    id: int
    product_id: int

    class Config:
        from_attributes = True

# ==================== PRODUCT SCHEMAS ====================
class ProductBase(BaseModel):
    title: str
    original_price: float
    discount_price: Optional[float] = None
    description: Optional[str] = None
    category_id: int
    brand_id: Optional[int] = None
    is_active: bool = True
    stock_quantity: int = 0

class ProductCreate(ProductBase):
    colors: List[ProductColorCreate] = []
    sizes: List[ProductSizeCreate] = []
    sub_images: List[ProductSubImageCreate] = []

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    original_price: Optional[float] = None
    discount_price: Optional[float] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    is_active: Optional[bool] = None
    stock_quantity: Optional[int] = None

class Product(ProductBase):
    id: int
    main_image: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[Category] = None
    brand: Optional[Brand] = None
    colors: List[ProductColor] = []
    sizes: List[ProductSize] = []
    sub_images: List[ProductSubImage] = []

    class Config:
        from_attributes = True

# ==================== BANNER SCHEMAS ====================
class BannerBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    link_url: Optional[str] = None
    order_position: int = 0
    is_active: bool = True

class BannerCreate(BannerBase):
    pass

class BannerUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    link_url: Optional[str] = None
    order_position: Optional[int] = None
    is_active: Optional[bool] = None

class Banner(BannerBase):
    id: int
    image_path: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== ORDER SCHEMAS ====================
class OrderItemBase(BaseModel):
    product_id: int
    product_name: str
    color: Optional[str] = None
    size: Optional[str] = None
    quantity: int
    price: float

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: str
    shipping_address: str
    payment_method: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]
    order_number: Optional[str] = None

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    payment_status: Optional[str] = None

class Order(OrderBase):
    id: int
    order_number: str
    total_amount: float
    status: str
    payment_status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[OrderItem] = []

    class Config:
        from_attributes = True
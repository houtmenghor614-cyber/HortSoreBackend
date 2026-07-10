from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import shutil
import uuid
import uvicorn

# ==================== APP SETUP ====================
app = FastAPI(title="Hor Phone Shop API", version="1.0.0")

# ==================== CORS ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== STATIC FILES ====================
uploads_dir = "uploads"
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)
    
# Create subdirectories
for subdir in ["products", "banners", "brands"]:
    sub_path = os.path.join(uploads_dir, subdir)
    if not os.path.exists(sub_path):
        os.makedirs(sub_path)

app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# ==================== IMAGE UPLOAD HELPER ====================
def save_upload_file(upload_file: UploadFile, sub_folder: str = "products") -> str:
    """Save uploaded file and return the path"""
    # Generate unique filename
    file_extension = os.path.splitext(upload_file.filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    
    # Create folder path
    folder_path = os.path.join(uploads_dir, sub_folder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Save file
    file_path = os.path.join(folder_path, unique_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return f"{sub_folder}/{unique_filename}"

# ==================== MODELS ====================
class Category(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime = datetime.now()

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class Brand(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    logo: Optional[str] = None
    created_at: datetime = datetime.now()

class BrandCreate(BaseModel):
    name: str
    description: Optional[str] = None
    logo: Optional[str] = None

class ProductColor(BaseModel):
    color_name: str
    color_code: Optional[str] = None

class ProductSize(BaseModel):
    size_name: str
    stock_quantity: int = 0

class Product(BaseModel):
    id: int
    title: str
    original_price: float
    discount_price: Optional[float] = None
    description: Optional[str] = None
    category_id: int
    brand_id: Optional[int] = None
    stock_quantity: int = 0
    is_active: bool = True
    main_image: Optional[str] = None
    sub_images: List[str] = []
    colors: List[ProductColor] = []
    sizes: List[ProductSize] = []
    created_at: datetime = datetime.now()

class ProductCreate(BaseModel):
    title: str
    original_price: float
    discount_price: Optional[float] = None
    description: Optional[str] = None
    category_id: int
    brand_id: Optional[int] = None
    stock_quantity: int = 0
    is_active: bool = True
    colors: List[ProductColor] = []
    sizes: List[ProductSize] = []

# ==================== BANNER MODELS (link_url removed) ====================
class Banner(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    image_path: str
    order_position: int = 0
    is_active: bool = True
    created_at: datetime = datetime.now()

class BannerCreate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_path: str
    order_position: int = 0
    is_active: bool = True

class OrderItem(BaseModel):
    product_id: int
    product_name: str
    color: Optional[str] = None
    size: Optional[str] = None
    quantity: int
    price: float

class Order(BaseModel):
    id: int
    order_number: str
    customer_name: str
    customer_email: str
    customer_phone: str
    shipping_address: str
    total_amount: float
    status: str = "pending"
    payment_status: str = "unpaid"
    items: List[OrderItem] = []
    created_at: datetime = datetime.now()

class OrderCreate(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: str
    shipping_address: str
    items: List[OrderItem]

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str

# ==================== DUMMY DATABASES ====================
categories_db = [
    Category(id=1, name="Smartphones", description="Mobile phones and accessories"),
    Category(id=2, name="Laptops", description="Laptops and computers"),
    Category(id=3, name="Accessories", description="Phone accessories and parts"),
]

brands_db = [
    Brand(id=1, name="Apple", description="Apple products", logo="brands/apple_logo.png"),
    Brand(id=2, name="Samsung", description="Samsung products", logo="brands/samsung_logo.png"),
    Brand(id=3, name="Xiaomi", description="Xiaomi products", logo="brands/xiaomi_logo.png"),
]

products_db = [
    Product(
        id=1, 
        title="iPhone 15 Pro", 
        original_price=999.00, 
        discount_price=899.00,
        description="Latest iPhone with amazing camera",
        category_id=1,
        brand_id=1,
        stock_quantity=10,
        main_image="products/iphone15_main.jpg",
        sub_images=["products/iphone15_1.jpg", "products/iphone15_2.jpg"],
        colors=[ProductColor(color_name="Black", color_code="#000000"), ProductColor(color_name="White", color_code="#FFFFFF")],
        sizes=[ProductSize(size_name="128GB", stock_quantity=5), ProductSize(size_name="256GB", stock_quantity=5)]
    ),
    Product(
        id=2, 
        title="Samsung Galaxy S24", 
        original_price=899.00, 
        discount_price=799.00,
        description="Latest Samsung with AI features",
        category_id=1,
        brand_id=2,
        stock_quantity=15,
        main_image="products/samsung_s24_main.jpg",
        sub_images=["products/samsung_s24_1.jpg", "products/samsung_s24_2.jpg"],
        colors=[ProductColor(color_name="Black", color_code="#000000"), ProductColor(color_name="Purple", color_code="#800080")],
        sizes=[ProductSize(size_name="128GB", stock_quantity=8), ProductSize(size_name="512GB", stock_quantity=7)]
    ),
]

# ==================== BANNERS DB (link_url removed) ====================
banners_db = [
    Banner(id=1, title="Summer Sale", description="Get up to 50% off", image_path="banners/summer_sale.jpg", order_position=1, is_active=True),
    Banner(id=2, title="New Arrivals", description="Check out our new products", image_path="banners/new_arrivals.jpg", order_position=2, is_active=True),
]

orders_db = []
order_counter = 1

# ==================== ADMIN AUTH ====================
@app.post("/api/admin/login", response_model=AdminToken)
async def admin_login(login_data: AdminLogin):
    if login_data.username == "admin" and login_data.password == "admin123":
        return AdminToken(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsInVzZXJuYW1lIjoiYWRtaW4ifQ.fake-token",
            username="admin"
        )
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/admin/verify")
async def verify_admin():
    return {"status": "authenticated", "user": "admin"}

# ==================== CATEGORIES CRUD ====================
@app.get("/api/categories", response_model=List[Category])
async def get_categories():
    return categories_db

@app.post("/api/categories", response_model=Category)
async def create_category(category: CategoryCreate):
    new_category = Category(
        id=len(categories_db) + 1,
        name=category.name,
        description=category.description
    )
    categories_db.append(new_category)
    return new_category

@app.put("/api/categories/{category_id}", response_model=Category)
async def update_category(category_id: int, category: CategoryCreate):
    for idx, cat in enumerate(categories_db):
        if cat.id == category_id:
            categories_db[idx].name = category.name
            categories_db[idx].description = category.description
            return categories_db[idx]
    raise HTTPException(status_code=404, detail="Category not found")

@app.delete("/api/categories/{category_id}")
async def delete_category(category_id: int):
    for idx, cat in enumerate(categories_db):
        if cat.id == category_id:
            categories_db.pop(idx)
            return {"message": "Category deleted successfully"}
    raise HTTPException(status_code=404, detail="Category not found")

# ==================== BRANDS CRUD ====================
@app.get("/api/brands", response_model=List[Brand])
async def get_brands():
    return brands_db

@app.post("/api/brands", response_model=Brand)
async def create_brand(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    logo: Optional[UploadFile] = File(None)
):
    logo_path = None
    if logo:
        logo_path = save_upload_file(logo, "brands")
    
    new_brand = Brand(
        id=len(brands_db) + 1,
        name=name,
        description=description,
        logo=logo_path
    )
    brands_db.append(new_brand)
    return new_brand

@app.put("/api/brands/{brand_id}", response_model=Brand)
async def update_brand(
    brand_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    logo: Optional[UploadFile] = File(None)
):
    for idx, b in enumerate(brands_db):
        if b.id == brand_id:
            if name:
                brands_db[idx].name = name
            if description is not None:
                brands_db[idx].description = description
            if logo:
                if brands_db[idx].logo:
                    old_path = os.path.join(uploads_dir, brands_db[idx].logo)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                brands_db[idx].logo = save_upload_file(logo, "brands")
            return brands_db[idx]
    raise HTTPException(status_code=404, detail="Brand not found")

@app.delete("/api/brands/{brand_id}")
async def delete_brand(brand_id: int):
    for idx, b in enumerate(brands_db):
        if b.id == brand_id:
            if b.logo:
                logo_path = os.path.join(uploads_dir, b.logo)
                if os.path.exists(logo_path):
                    os.remove(logo_path)
            brands_db.pop(idx)
            return {"message": "Brand deleted successfully"}
    raise HTTPException(status_code=404, detail="Brand not found")

# ==================== PRODUCTS CRUD ====================
@app.get("/api/products", response_model=List[Product])
async def get_products():
    return products_db

@app.get("/api/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    for product in products_db:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/api/products")
async def create_product(
    title: str = Form(...),
    original_price: float = Form(...),
    discount_price: Optional[float] = Form(None),
    description: Optional[str] = Form(None),
    category_id: int = Form(...),
    brand_id: Optional[int] = Form(None),
    stock_quantity: int = Form(0),
    is_active: bool = Form(True),
    colors: Optional[str] = Form('[]'),
    sizes: Optional[str] = Form('[]'),
    main_image: Optional[UploadFile] = File(None),
    sub_images: List[UploadFile] = File([])
):
    import json
    
    colors_list = json.loads(colors) if colors else []
    sizes_list = json.loads(sizes) if sizes else []
    
    main_image_path = None
    if main_image:
        main_image_path = save_upload_file(main_image, "products")
    
    sub_images_paths = []
    for img in sub_images:
        if img and img.filename:
            path = save_upload_file(img, "products")
            sub_images_paths.append(path)
    
    new_product = Product(
        id=len(products_db) + 1,
        title=title,
        original_price=original_price,
        discount_price=discount_price,
        description=description,
        category_id=category_id,
        brand_id=brand_id,
        stock_quantity=stock_quantity,
        is_active=is_active,
        main_image=main_image_path,
        sub_images=sub_images_paths,
        colors=[ProductColor(**c) for c in colors_list],
        sizes=[ProductSize(**s) for s in sizes_list]
    )
    products_db.append(new_product)
    return new_product

@app.put("/api/products/{product_id}")
async def update_product(
    product_id: int,
    title: Optional[str] = Form(None),
    original_price: Optional[float] = Form(None),
    discount_price: Optional[float] = Form(None),
    description: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    brand_id: Optional[int] = Form(None),
    stock_quantity: Optional[int] = Form(None),
    is_active: Optional[bool] = Form(None),
    colors: Optional[str] = Form(None),
    sizes: Optional[str] = Form(None),
    main_image: Optional[UploadFile] = File(None),
    sub_images: List[UploadFile] = File([])
):
    import json
    
    for idx, p in enumerate(products_db):
        if p.id == product_id:
            if title:
                products_db[idx].title = title
            if original_price is not None:
                products_db[idx].original_price = original_price
            if discount_price is not None:
                products_db[idx].discount_price = discount_price
            if description is not None:
                products_db[idx].description = description
            if category_id is not None:
                products_db[idx].category_id = category_id
            if brand_id is not None:
                products_db[idx].brand_id = brand_id
            if stock_quantity is not None:
                products_db[idx].stock_quantity = stock_quantity
            if is_active is not None:
                products_db[idx].is_active = is_active
            if colors:
                colors_list = json.loads(colors)
                products_db[idx].colors = [ProductColor(**c) for c in colors_list]
            if sizes:
                sizes_list = json.loads(sizes)
                products_db[idx].sizes = [ProductSize(**s) for s in sizes_list]
            if main_image:
                if products_db[idx].main_image:
                    old_path = os.path.join(uploads_dir, products_db[idx].main_image)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                products_db[idx].main_image = save_upload_file(main_image, "products")
            if sub_images:
                for img in sub_images:
                    if img and img.filename:
                        path = save_upload_file(img, "products")
                        products_db[idx].sub_images.append(path)
            return products_db[idx]
    raise HTTPException(status_code=404, detail="Product not found")

@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int):
    for idx, p in enumerate(products_db):
        if p.id == product_id:
            if p.main_image:
                main_path = os.path.join(uploads_dir, p.main_image)
                if os.path.exists(main_path):
                    os.remove(main_path)
            for sub_img in p.sub_images:
                sub_path = os.path.join(uploads_dir, sub_img)
                if os.path.exists(sub_path):
                    os.remove(sub_path)
            products_db.pop(idx)
            return {"message": "Product deleted successfully"}
    raise HTTPException(status_code=404, detail="Product not found")

# ==================== BANNERS CRUD (link_url removed) ====================
@app.get("/api/banners", response_model=List[Banner])
async def get_banners(is_active: Optional[bool] = None):
    if is_active is not None:
        return [b for b in banners_db if b.is_active == is_active]
    return banners_db

@app.get("/api/banners/{banner_id}", response_model=Banner)
async def get_banner(banner_id: int):
    for banner in banners_db:
        if banner.id == banner_id:
            return banner
    raise HTTPException(status_code=404, detail="Banner not found")

@app.post("/api/banners")
async def create_banner(
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    order_position: int = Form(0),
    is_active: bool = Form(True),
    image: UploadFile = File(...)
):
    image_path = save_upload_file(image, "banners")
    
    new_banner = Banner(
        id=len(banners_db) + 1,
        title=title,
        description=description,
        image_path=image_path,
        order_position=order_position,
        is_active=is_active
    )
    banners_db.append(new_banner)
    return new_banner

@app.put("/api/banners/{banner_id}")
async def update_banner(
    banner_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    order_position: Optional[int] = Form(None),
    is_active: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None)
):
    for idx, b in enumerate(banners_db):
        if b.id == banner_id:
            if title is not None:
                banners_db[idx].title = title
            if description is not None:
                banners_db[idx].description = description
            if order_position is not None:
                banners_db[idx].order_position = order_position
            if is_active is not None:
                banners_db[idx].is_active = is_active
            if image:
                if banners_db[idx].image_path:
                    old_path = os.path.join(uploads_dir, banners_db[idx].image_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                banners_db[idx].image_path = save_upload_file(image, "banners")
            return banners_db[idx]
    raise HTTPException(status_code=404, detail="Banner not found")

@app.delete("/api/banners/{banner_id}")
async def delete_banner(banner_id: int):
    for idx, b in enumerate(banners_db):
        if b.id == banner_id:
            if b.image_path:
                img_path = os.path.join(uploads_dir, b.image_path)
                if os.path.exists(img_path):
                    os.remove(img_path)
            banners_db.pop(idx)
            return {"message": "Banner deleted successfully"}
    raise HTTPException(status_code=404, detail="Banner not found")

# ==================== ORDERS CRUD ====================
@app.get("/api/orders", response_model=List[Order])
async def get_orders():
    return orders_db

@app.get("/api/orders/{order_id}", response_model=Order)
async def get_order(order_id: int):
    for order in orders_db:
        if order.id == order_id:
            return order
    raise HTTPException(status_code=404, detail="Order not found")

@app.post("/api/orders", response_model=Order)
async def create_order(order: OrderCreate):
    global order_counter
    total = sum(item.price * item.quantity for item in order.items)
    new_order = Order(
        id=order_counter,
        order_number=f"ORD-{order_counter:04d}",
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        customer_phone=order.customer_phone,
        shipping_address=order.shipping_address,
        total_amount=total,
        items=order.items
    )
    order_counter += 1
    orders_db.append(new_order)
    return new_order

@app.put("/api/orders/{order_id}", response_model=Order)
async def update_order_status(order_id: int, status: str):
    for idx, o in enumerate(orders_db):
        if o.id == order_id:
            orders_db[idx].status = status
            return orders_db[idx]
    raise HTTPException(status_code=404, detail="Order not found")

@app.delete("/api/orders/{order_id}")
async def delete_order(order_id: int):
    for idx, o in enumerate(orders_db):
        if o.id == order_id:
            orders_db.pop(idx)
            return {"message": "Order deleted successfully"}
    raise HTTPException(status_code=404, detail="Order not found")

# ==================== HEALTH CHECK ====================
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Hor Phone Shop API is running"}

@app.get("/")
async def root():
    return {
        "message": "Hor Phone Shop API",
        "version": "1.0.0",
        "endpoints": {
            "categories": "/api/categories",
            "brands": "/api/brands",
            "products": "/api/products",
            "banners": "/api/banners",
            "orders": "/api/orders",
            "admin_login": "/api/admin/login",
            "admin_verify": "/api/admin/verify",
            "health": "/api/health",
            "docs": "/docs"
        }
    }

# ==================== RUN ====================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
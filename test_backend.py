from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI()

# CORS - Allow everything
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MODELS ====================
class Category(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime = datetime.now()

class Brand(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    logo: Optional[str] = None
    created_at: datetime = datetime.now()

# ==================== DUMMY DATA ====================
categories_db = [
    Category(id=1, name="Smartphones", description="Mobile phones and accessories"),
    Category(id=2, name="Laptops", description="Laptops and computers"),
    Category(id=3, name="Accessories", description="Phone accessories and parts"),
]

brands_db = [
    Brand(id=1, name="Apple", description="Apple products"),
    Brand(id=2, name="Samsung", description="Samsung products"),
    Brand(id=3, name="Xiaomi", description="Xiaomi products"),
]

# ==================== ADMIN LOGIN ====================
class AdminLogin(BaseModel):
    username: str
    password: str

class AdminToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str

@app.post("/api/admin/login")
async def admin_login(login_data: AdminLogin):
    if login_data.username == "admin" and login_data.password == "admin123":
        return AdminToken(
            access_token="fake-token-12345",
            username="admin"
        )
    return {"error": "Invalid credentials"}

@app.get("/api/admin/verify")
async def verify_admin():
    return {"status": "authenticated", "user": "admin"}

# ==================== CATEGORIES ====================
@app.get("/api/categories", response_model=List[Category])
async def get_categories():
    return categories_db

@app.post("/api/categories", response_model=Category)
async def create_category(category: Category):
    new_category = Category(
        id=len(categories_db) + 1,
        name=category.name,
        description=category.description
    )
    categories_db.append(new_category)
    return new_category

@app.delete("/api/categories/{category_id}")
async def delete_category(category_id: int):
    global categories_db
    categories_db = [c for c in categories_db if c.id != category_id]
    return {"message": "Category deleted"}

# ==================== BRANDS ====================
@app.get("/api/brands", response_model=List[Brand])
async def get_brands():
    return brands_db

@app.post("/api/brands", response_model=Brand)
async def create_brand(brand: Brand):
    new_brand = Brand(
        id=len(brands_db) + 1,
        name=brand.name,
        description=brand.description,
        logo=brand.logo
    )
    brands_db.append(new_brand)
    return new_brand

@app.delete("/api/brands/{brand_id}")
async def delete_brand(brand_id: int):
    global brands_db
    brands_db = [b for b in brands_db if b.id != brand_id]
    return {"message": "Brand deleted"}

# ==================== HEALTH ====================
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Test API is running"}

@app.get("/")
async def root():
    return {
        "message": "Hor Phone Shop API (Test Version)",
        "endpoints": {
            "categories": "/api/categories",
            "brands": "/api/brands",
            "admin_login": "/api/admin/login",
            "health": "/api/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
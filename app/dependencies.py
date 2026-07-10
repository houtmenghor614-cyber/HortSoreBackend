from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import os
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Admin credentials (in production, store in database)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

class AdminAuth:
    """Admin authentication class"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

admin_auth = AdminAuth()

# Dependency for admin authentication
async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current admin from token"""
    token = credentials.credentials
    payload = admin_auth.verify_token(token)
    
    # Check if user is admin
    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    return payload

async def validate_admin_login(username: str, password: str) -> Optional[str]:
    """Validate admin login credentials"""
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        # Create token
        token_data = {
            "sub": username,
            "role": "admin",
            "username": username
        }
        token = admin_auth.create_access_token(token_data)
        return token
    return None

# Dependency for optional admin authentication
async def get_optional_admin(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """Get admin if authenticated, else None"""
    try:
        if credentials:
            token = credentials.credentials
            payload = admin_auth.verify_token(token)
            if payload.get("role") == "admin":
                return payload
    except Exception:
        pass
    return None

# Rate limiting dependency
class RateLimiter:
    """Simple rate limiter for API endpoints"""
    
    def __init__(self):
        self.requests = {}  # IP: [timestamps]
        self.limit = 60  # requests per minute
        self.window = 60  # seconds
    
    def check_rate_limit(self, client_ip: str) -> bool:
        """Check if client is rate limited"""
        now = datetime.now().timestamp()
        
        if client_ip not in self.requests:
            self.requests[client_ip] = [now]
            return True
        
        # Clean old requests
        self.requests[client_ip] = [
            timestamp for timestamp in self.requests[client_ip]
            if now - timestamp < self.window
        ]
        
        # Check limit
        if len(self.requests[client_ip]) >= self.limit:
            return False
        
        self.requests[client_ip].append(now)
        return True

rate_limiter = RateLimiter()

async def check_rate_limit(request, client_ip: str = None):
    """Rate limit dependency"""
    if not client_ip:
        client_ip = request.client.host
    
    if not rate_limiter.check_rate_limit(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )
    return True

# Pagination dependency
class Pagination:
    def __init__(self, page: int = 1, page_size: int = 20):
        self.page = max(1, page)
        self.page_size = min(100, max(1, page_size))
        self.offset = (self.page - 1) * self.page_size
    
    @property
    def skip(self) -> int:
        return self.offset
    
    @property
    def limit(self) -> int:
        return self.page_size

async def get_pagination(page: int = 1, page_size: int = 20) -> Pagination:
    """Get pagination parameters"""
    return Pagination(page=page, page_size=page_size)

# File validation dependency
class FileValidator:
    """Validate uploaded files"""
    
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    ALLOWED_DOCUMENT_EXTENSIONS = {'.pdf', '.doc', '.docx'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    @staticmethod
    def validate_image(filename: str, content_length: int) -> bool:
        """Validate image file"""
        ext = os.path.splitext(filename)[1].lower()
        if ext not in FileValidator.ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type {ext} not allowed. Allowed types: {', '.join(FileValidator.ALLOWED_IMAGE_EXTENSIONS)}"
            )
        
        if content_length > FileValidator.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size too large. Maximum size: {FileValidator.MAX_FILE_SIZE // 1024 // 1024}MB"
            )
        
        return True
    
    @staticmethod
    def validate_document(filename: str, content_length: int) -> bool:
        """Validate document file"""
        ext = os.path.splitext(filename)[1].lower()
        if ext not in FileValidator.ALLOWED_DOCUMENT_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type {ext} not allowed. Allowed types: {', '.join(FileValidator.ALLOWED_DOCUMENT_EXTENSIONS)}"
            )
        
        if content_length > FileValidator.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size too large. Maximum size: {FileValidator.MAX_FILE_SIZE // 1024 // 1024}MB"
            )
        
        return True

file_validator = FileValidator()

# Database transaction dependency
async def transaction_dependency(db: Session):
    """Handle database transactions"""
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# Cache dependency (simple in-memory cache)
class Cache:
    """Simple in-memory cache for frequently accessed data"""
    
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def get(self, key: str):
        """Get value from cache"""
        if key in self._cache:
            if self._expiry.get(key, 0) > datetime.now().timestamp():
                return self._cache[key]
            else:
                # Remove expired
                del self._cache[key]
                del self._expiry[key]
        return None
    
    def set(self, key: str, value, ttl_seconds: int = 300):
        """Set value in cache with TTL"""
        self._cache[key] = value
        self._expiry[key] = datetime.now().timestamp() + ttl_seconds
    
    def delete(self, key: str):
        """Delete from cache"""
        if key in self._cache:
            del self._cache[key]
            del self._expiry[key]
    
    def clear(self):
        """Clear entire cache"""
        self._cache.clear()
        self._expiry.clear()

cache = Cache()

# Dependency for cache
def get_cache():
    """Get cache instance"""
    return cache
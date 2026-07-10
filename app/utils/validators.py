import re
from typing import Optional

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate phone number"""
    pattern = r'^\+?[\d\s-]{8,20}$'
    return bool(re.match(pattern, phone))

def validate_price(price: float) -> bool:
    """Validate price is positive"""
    return price >= 0

def validate_quantity(quantity: int) -> bool:
    """Validate quantity is positive integer"""
    return quantity > 0
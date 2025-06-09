from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # For SQLAlchemy model compatibility

class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    total: int

class ProductMessageResponse(BaseModel):
    message: str
    product_id: Optional[int] = None
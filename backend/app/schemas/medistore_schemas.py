# app/schemas/medistore_schemas.py
from typing import Optional, List
from pydantic import BaseModel, Field
from ..models.medistore import PharmacyOrderStatus

class MedicineCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    description: Optional[str] = None
    price: float = Field(..., ge=0.0)
    stock: int = Field(..., ge=0)
    category: str = Field(..., min_length=2, max_length=50)
    manufacturer: Optional[str] = None

class MedicineUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0.0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = None
    manufacturer: Optional[str] = None

class CartItemSchema(BaseModel):
    medicine_id: str
    quantity: int = Field(..., ge=1)

class OrderCreateSchema(BaseModel):
    patient_id: Optional[str] = None
    shipping_address: str = Field(..., min_length=5, max_length=255)
    phone_number: str = Field(..., min_length=5, max_length=15)
    items: List[CartItemSchema] = Field(..., min_length=1)

class OrderStatusUpdateSchema(BaseModel):
    status: PharmacyOrderStatus

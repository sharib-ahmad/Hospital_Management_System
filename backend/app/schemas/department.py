# app/schemas/department.py
from typing import Optional
from pydantic import BaseModel, Field

class DepartmentCreateSchema(BaseModel):
    id: str = Field(..., min_length=6, max_length=12)
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    doctor_limit: Optional[int] = Field(3, ge=0)
    nurse_limit: Optional[int] = Field(5, ge=0)

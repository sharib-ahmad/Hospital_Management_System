# app/schemas/doctor.py
from typing import Optional, Annotated
from pydantic import BaseModel, Field
from decimal import Decimal

class DepartmentCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class DoctorCreateSchema(BaseModel):
    user_id: str
    specialization: str = Field(..., min_length=2, max_length=100)
    experience_years: Optional[int] = Field(0, ge=0)
    consultation_fee: Annotated[
        Decimal,
        Field(max_digits=10, decimal_places=2)
    ]
    department_id: int

class DoctorUpdateSchema(BaseModel):
    specialization: Optional[str] = Field(None, min_length=2, max_length=100)
    experience_years: Optional[int] = Field(None, ge=0)

    consultation_fee: Optional[
        Annotated[
            Decimal,
            Field(max_digits=10, decimal_places=2)
        ]
    ] = None

    is_available: Optional[bool] = None
    department_id: Optional[int] = None

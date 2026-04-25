# app/schemas/doctor.py
from typing import Optional, Annotated
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import date
from ..utils.enum import Gender, BloodGroup

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
    department_id: Optional[str] = None
    gender: Optional[Gender] = None
    blood_group: Optional[BloodGroup] = None
    shift: Optional[str] = None
    emergency_contact_number: Optional[str] = None

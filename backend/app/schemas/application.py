from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from decimal import Decimal
from ..utils.enum import Gender, BloodGroup

class BaseApplicationSchema(BaseModel):
    reason: str = Field(..., min_length=5)
    date_of_birth: date
    gender: Gender
    blood_group: BloodGroup
    emergency_contact_number: str = Field(..., max_length=15)

class PatientApplicationCreateSchema(BaseApplicationSchema):
    medical_history: Optional[str] = None

class DoctorApplicationCreateSchema(BaseApplicationSchema):
    specialization: str = Field(..., max_length=100)
    experience_years: int = Field(..., ge=0)
    consultation_fee: Decimal = Field(..., ge=0)
    license_number: str = Field(...,min_length=12, max_length=20)
    department_id: str = Field(..., max_length=12)
    shift: str = Field(..., max_length=20)

class NurseApplicationCreateSchema(BaseApplicationSchema):
    experience_years: int = Field(..., ge=0)
    license_number: str = Field(...,min_length=12, max_length=20)
    department_id: str = Field(..., max_length=12)
    shift: str = Field(..., max_length=20)

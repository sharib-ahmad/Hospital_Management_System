# app/schemas/nurse.py
from typing import Optional
from pydantic import BaseModel, Field
from ..utils.enum import Gender, BloodGroup

class NurseUpdateSchema(BaseModel):
    experience_years: Optional[int] = Field(None, ge=0)
    is_available: Optional[bool] = None
    department_id: Optional[str] = None
    gender: Optional[Gender] = None
    blood_group: Optional[BloodGroup] = None
    shift: Optional[str] = None
    emergency_contact_number: Optional[str] = None
    availability: Optional[dict] = None

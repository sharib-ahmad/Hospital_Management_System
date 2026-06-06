from typing import Optional
from pydantic import BaseModel, Field
from ..utils.enum import Gender, BloodGroup

class PharmacistUpdateSchema(BaseModel):
    experience_years: Optional[int] = Field(None, ge=0)
    is_available: Optional[bool] = None
    gender: Optional[Gender] = None
    blood_group: Optional[BloodGroup] = None
    shift: Optional[str] = None
    emergency_contact_number: Optional[str] = None
    availability: Optional[dict] = None

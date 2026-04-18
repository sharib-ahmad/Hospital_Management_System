from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Literal

class UserRegisterSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    full_name: str = Field(..., min_length=3, max_length=128)
    email: EmailStr

    address: Optional[str] = Field(None, max_length=256)
    phone_number: Optional[str] = Field(None, max_length=20)
    pincode: Optional[str] = Field(None, max_length=10)

    password: str = Field(..., min_length=6, max_length=128)

    role: Literal["admin", "doctor", "receptionist", "nurse", "patient"] = "patient"

    @field_validator("username")
    def normalize_username(cls, v):
        return v.lower()

    @field_validator("email")
    def normalize_email(cls, v):
        return v.lower()


class UserLoginSchema(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
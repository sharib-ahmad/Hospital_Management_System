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


    @field_validator("username")
    def normalize_username(cls, v):
        return v.lower()

    @field_validator("email")
    def normalize_email(cls, v):
        return v.lower()

    @field_validator("phone_number")
    def validate_phone_unique(cls, v):
        if v:
            from app.models.user import User
            if User.query.filter_by(phone_number=v).first():
                raise ValueError("Phone number already registered")
        return v


class UserLoginSchema(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
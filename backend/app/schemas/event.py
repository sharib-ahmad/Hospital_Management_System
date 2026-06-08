from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class EventCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = None
    event_date: datetime
    event_type: str = Field(..., min_length=1, max_length=50)  # meeting, occasion, ceremony, etc.
    location: Optional[str] = Field(None, max_length=120)

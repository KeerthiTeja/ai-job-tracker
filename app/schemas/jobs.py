from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class JobCreate(BaseModel):
    company: str
    title: str
    country: str
    location: str
    status: str = Field(pattern="^(wishlist|applied|interview|offer|rejected)$")
    url: str | None = None
    description: str

class JobOut(BaseModel):
    id: int
    company: str
    title: str
    country: str
    location: str
    status: str
    url: str | None
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

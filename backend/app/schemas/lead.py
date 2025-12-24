from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class LeadBase(BaseModel):
    source: str
    campaign: Optional[str] = None
    channel: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_e164: Optional[str] = None
    contact_pref: Optional[str] = None
    consent: bool = False
    message: Optional[str] = None
    project_type: Optional[str] = None
    typology: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    zipcode: Optional[str] = None
    city: Optional[str] = None
    origin: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadRead(LeadBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

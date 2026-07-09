from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from models import IssueStatus, WorkerCategory, WorkerStatus

PHONE_FIELD = Field(min_length=7, max_length=15, pattern=r"^\+?[0-9]+$")
NON_EMPTY_TEXT = Field(min_length=1, max_length=255)
PASSWORD_FIELD = Field(min_length=6, max_length=72)


def _clean_decimal(v):
    if isinstance(v, float):
        return Decimal(str(round(v, 6)))
    return v


# ---------- Client ----------

class ClientCreate(BaseModel):
    name: str = NON_EMPTY_TEXT
    home_address_text: str = NON_EMPTY_TEXT
    phone: str = PHONE_FIELD
    password: str = PASSWORD_FIELD
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ClientLogin(BaseModel):
    phone: str
    password: str


class Client(BaseModel):
    client_id: int
    name: str
    home_address_text: str
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    phone: str

    _clean_latitude = field_validator("latitude", mode="before")(_clean_decimal)
    _clean_longitude = field_validator("longitude", mode="before")(_clean_decimal)

    class Config:
        from_attributes = True


# ---------- Worker ----------

class WorkerCreate(BaseModel):
    name: str = NON_EMPTY_TEXT
    age: int = Field(ge=18, le=100)
    experience_years: int = Field(ge=0, le=80)
    category: WorkerCategory
    location_text: str = NON_EMPTY_TEXT
    photo_url: Optional[str] = None
    phone: str = PHONE_FIELD
    password: str = PASSWORD_FIELD
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class WorkerLogin(BaseModel):
    phone: str
    password: str


class WorkerStatusUpdate(BaseModel):
    status: WorkerStatus


class Worker(BaseModel):
    worker_id: int
    name: str
    age: int
    experience_years: int
    category: WorkerCategory
    location_text: str
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    photo_url: Optional[str] = None
    phone: str
    status: WorkerStatus

    _clean_latitude = field_validator("latitude", mode="before")(_clean_decimal)
    _clean_longitude = field_validator("longitude", mode="before")(_clean_decimal)

    class Config:
        from_attributes = True


# ---------- Issue (Job) ----------

class IssueCreate(BaseModel):
    category: WorkerCategory
    description: str = Field(min_length=1, max_length=2000)
    photo_url: Optional[str] = None
    location_text: str = NON_EMPTY_TEXT
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class Issue(BaseModel):
    issue_id: int
    client_id: int
    category: WorkerCategory
    description: str
    photo_url: Optional[str] = None
    location_text: str
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    status: IssueStatus
    accepted_by: Optional[int] = None
    created_at: datetime
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    _clean_latitude = field_validator("latitude", mode="before")(_clean_decimal)
    _clean_longitude = field_validator("longitude", mode="before")(_clean_decimal)

    class Config:
        from_attributes = True


# ---------- Auth ----------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64, examples=["test"])
    password: str = Field(min_length=1, max_length=72, examples=["1111"])


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64, examples=["maria"])
    password: str = Field(min_length=1, max_length=72, examples=["1111"])


class OrganizerOut(BaseModel):
    id: int
    name: str
    role: str


class MyApplicationBrief(BaseModel):
    id: int
    status: str
    status_label: str


class MarketOut(BaseModel):
    id: str
    title: str
    city: str
    venue_name: str | None
    address: str | None
    description: str
    image: str
    tags: list[str]
    start_date: str
    end_date: str
    opens_at: str
    closes_at: str
    meta: str
    detail_meta: str
    latitude: float | None
    longitude: float | None
    organizer: OrganizerOut | None
    is_favorite: bool
    my_application: MyApplicationBrief | None


class ResumeIn(BaseModel):
    nickname: str = Field(min_length=1, max_length=120)
    real_name: str = ""
    about: str = ""
    telegram: str | None = None
    phone: str | None = None
    email: str | None = None
    photos: list[str | None] = Field(default_factory=list)


class ResumePatch(BaseModel):
    nickname: str | None = None
    real_name: str | None = None
    about: str | None = None
    telegram: str | None = None
    phone: str | None = None
    email: str | None = None
    photos: list[str | None] | None = None


class ResumeOut(BaseModel):
    id: int
    nickname: str
    real_name: str
    about: str
    telegram: str | None
    phone: str | None
    email: str | None
    photos: list[str | None]
    photo_count: int


class ApplicationCreate(BaseModel):
    market_id: str = Field(min_length=1, max_length=64, examples=["art-dvor"])
    resume_id: int
    message: str = ""


class ApplicationOut(BaseModel):
    id: int
    status: str
    status_label: str
    message: str
    resume_id: int
    created_at: datetime
    market: MarketOut


class ProfileOut(BaseModel):
    id: int
    username: str
    display_name: str
    role: str
    city: str
    notifications_enabled: bool
    cabinet_name: str
    resumes_count: int


class ProfilePatch(BaseModel):
    display_name: str | None = Field(default=None, max_length=120)
    role: str | None = Field(default=None, max_length=80)
    city: str | None = Field(default=None, max_length=120)
    notifications_enabled: bool | None = None


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: ProfileOut

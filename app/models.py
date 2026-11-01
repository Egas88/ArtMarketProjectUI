from datetime import date, datetime, time

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(80), default="Художник / Мастер")
    city: Mapped[str] = mapped_column(String(120), default="Санкт-Петербург")
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    resumes: Mapped[list["Resume"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Resume.id",
    )


class Organizer(Base):
    __tablename__ = "organizers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(80), default="Организатор")

    markets: Mapped[list["Market"]] = relationship(back_populates="organizer")


class Market(Base):
    __tablename__ = "markets"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    city: Mapped[str] = mapped_column(String(120), index=True)
    venue_name: Mapped[str | None] = mapped_column(String(200))
    address: Mapped[str | None] = mapped_column(String(300))
    image: Mapped[str] = mapped_column(String(120), default="")
    tags: Mapped[list] = mapped_column(JSONB, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, index=True)
    end_date: Mapped[date] = mapped_column(Date)
    opens_at: Mapped[time] = mapped_column(Time)
    closes_at: Mapped[time] = mapped_column(Time)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    organizer_id: Mapped[int | None] = mapped_column(ForeignKey("organizers.id"))

    organizer: Mapped[Organizer | None] = relationship(back_populates="markets", lazy="selectin")


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    nickname: Mapped[str] = mapped_column(String(120))
    real_name: Mapped[str] = mapped_column(String(120), default="")
    about: Mapped[str] = mapped_column(Text, default="")
    telegram: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(64))
    email: Mapped[str | None] = mapped_column(String(255))
    photos: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped[User] = relationship(back_populates="resumes")


class Favorite(Base):
    __tablename__ = "favorites"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    market_id: Mapped[str] = mapped_column(ForeignKey("markets.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    market: Mapped[Market] = relationship(lazy="selectin")


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("user_id", "market_id", name="uq_application_user_market"),
        CheckConstraint(
            "status IN ('pending', 'participating', 'rejected')",
            name="ck_application_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    market_id: Mapped[str] = mapped_column(ForeignKey("markets.id", ondelete="CASCADE"), index=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id", ondelete="RESTRICT"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    message: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship()
    market: Mapped[Market] = relationship(lazy="selectin")
    resume: Mapped[Resume] = relationship()

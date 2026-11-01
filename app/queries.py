from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Application, Favorite, Market, Resume, User


def favorite_ids_for(db: Session, user: User | None) -> set[str]:
    if user is None:
        return set()
    rows = db.scalars(select(Favorite.market_id).where(Favorite.user_id == user.id))
    return set(rows)


def applications_for(db: Session, user: User | None) -> dict[str, Application]:
    if user is None:
        return {}
    rows = db.scalars(select(Application).where(Application.user_id == user.id))
    return {row.market_id: row for row in rows}


def get_market_or_404(db: Session, market_id: str) -> Market:
    market = db.get(Market, market_id)
    if market is None:
        raise HTTPException(status_code=404, detail="Маркет не найден")
    return market


def get_resume_or_404(db: Session, user: User, resume_id: int) -> Resume:
    resume = db.get(Resume, resume_id)
    if resume is None or resume.user_id != user.id:
        raise HTTPException(status_code=404, detail="Резюме не найдено")
    return resume

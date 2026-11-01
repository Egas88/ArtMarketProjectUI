from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import Application, Resume, User
from app.presenters import dump_resume
from app.queries import get_resume_or_404
from app.schemas import ResumeIn, ResumeOut, ResumePatch

router = APIRouter()


def _clean_optional(value: str | None, *, limit: int, too_long: str) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    if len(value) > limit:
        raise HTTPException(status_code=400, detail=too_long)
    return value


def _clean_text(value: str, *, limit: int, too_long: str) -> str:
    value = value.strip()
    if len(value) > limit:
        raise HTTPException(status_code=400, detail=too_long)
    return value


def _clean_email(value: str | None) -> str | None:
    email = _clean_optional(value, limit=255, too_long="Email слишком длинный")
    if email and "@" not in email:
        raise HTTPException(status_code=400, detail="Некорректный email")
    return email


def _clean_photos(photos: list[str | None]) -> list[str | None]:
    if len(photos) > 6:
        raise HTTPException(status_code=400, detail="Можно прикрепить не больше 6 фото")
    cleaned: list[str | None] = []
    for item in photos:
        if item is None:
            cleaned.append(None)
            continue
        item = item.strip()
        if not item:
            cleaned.append(None)
            continue
        if len(item) > 500:
            raise HTTPException(status_code=400, detail="Ссылка на фото слишком длинная")
        cleaned.append(item)
    return cleaned


def _apply_resume_fields(resume: Resume, payload: ResumeIn | ResumePatch, *, partial: bool) -> None:
    data = payload.model_dump(exclude_unset=True) if partial else payload.model_dump()
    if not data:
        return
    if "nickname" in data:
        nickname = (data["nickname"] or "").strip()
        if not nickname:
            raise HTTPException(status_code=400, detail="Укажите никнейм или бренд")
        if len(nickname) > 120:
            raise HTTPException(status_code=400, detail="Никнейм слишком длинный")
        resume.nickname = nickname
    if "real_name" in data:
        resume.real_name = _clean_text(data["real_name"] or "", limit=120, too_long="Имя слишком длинное")
    if "about" in data:
        resume.about = _clean_text(data["about"] or "", limit=4000, too_long="Описание слишком длинное")
    if "telegram" in data:
        resume.telegram = _clean_optional(data["telegram"], limit=255, too_long="Telegram слишком длинный")
    if "phone" in data:
        resume.phone = _clean_optional(data["phone"], limit=64, too_long="Телефон слишком длинный")
    if "email" in data:
        resume.email = _clean_email(data["email"])
    if "photos" in data and data["photos"] is not None:
        resume.photos = _clean_photos(data["photos"])
    resume.updated_at = datetime.now(timezone.utc)


@router.get("", response_model=list[ResumeOut])
def list_resumes(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ResumeOut]:
    resumes = db.scalars(select(Resume).where(Resume.user_id == user.id).order_by(Resume.id)).all()
    return [ResumeOut(**dump_resume(resume)) for resume in resumes]


@router.post("", response_model=ResumeOut, status_code=201)
def create_resume(
    payload: ResumeIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ResumeOut:
    resume = Resume(user_id=user.id, nickname="Новый бренд", photos=[])
    _apply_resume_fields(resume, payload, partial=False)
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return ResumeOut(**dump_resume(resume))


@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ResumeOut:
    return ResumeOut(**dump_resume(get_resume_or_404(db, user, resume_id)))


@router.patch("/{resume_id}", response_model=ResumeOut)
def update_resume(
    resume_id: int,
    payload: ResumePatch,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ResumeOut:
    resume = get_resume_or_404(db, user, resume_id)
    _apply_resume_fields(resume, payload, partial=True)
    db.commit()
    db.refresh(resume)
    return ResumeOut(**dump_resume(resume))


@router.delete("/{resume_id}", status_code=204)
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    resume = get_resume_or_404(db, user, resume_id)
    used = db.scalar(
        select(func.count()).select_from(Application).where(Application.resume_id == resume.id)
    )
    if used:
        raise HTTPException(status_code=409, detail="Нельзя удалить резюме, по которому есть заявка")
    db.delete(resume)
    db.commit()

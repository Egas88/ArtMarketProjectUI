from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import Application, User
from app.presenters import dump_application
from app.queries import applications_for, favorite_ids_for, get_market_or_404, get_resume_or_404
from app.schemas import ApplicationCreate, ApplicationOut

router = APIRouter()


def _dump(db: Session, user: User, application: Application) -> ApplicationOut:
    return ApplicationOut(
        **dump_application(
            application,
            favorite_ids=favorite_ids_for(db, user),
            applications=applications_for(db, user),
        )
    )


@router.get("", response_model=list[ApplicationOut])
def list_applications(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ApplicationOut]:
    rows = db.scalars(
        select(Application).where(Application.user_id == user.id).order_by(Application.id)
    ).all()
    favorite_ids = favorite_ids_for(db, user)
    applications = {row.market_id: row for row in rows}
    return [
        ApplicationOut(
            **dump_application(row, favorite_ids=favorite_ids, applications=applications)
        )
        for row in rows
    ]


@router.post("", response_model=ApplicationOut, status_code=201)
def create_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApplicationOut:
    message = payload.message.strip()
    if len(message) > 2000:
        raise HTTPException(status_code=400, detail="Сообщение слишком длинное")
    get_market_or_404(db, payload.market_id)
    get_resume_or_404(db, user, payload.resume_id)
    existing = db.scalar(
        select(Application).where(
            Application.user_id == user.id,
            Application.market_id == payload.market_id,
        )
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="Заявка на этот маркет уже отправлена")

    application = Application(
        user_id=user.id,
        market_id=payload.market_id,
        resume_id=payload.resume_id,
        status="pending",
        message=message,
    )
    db.add(application)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Заявка на этот маркет уже отправлена") from None
    db.refresh(application)
    return _dump(db, user, application)


@router.get("/{application_id}", response_model=ApplicationOut)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApplicationOut:
    application = db.get(Application, application_id)
    if application is None or application.user_id != user.id:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return _dump(db, user, application)

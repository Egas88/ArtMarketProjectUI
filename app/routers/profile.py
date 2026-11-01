from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import User
from app.presenters import dump_profile
from app.schemas import ProfileOut, ProfilePatch

router = APIRouter()


@router.get("", response_model=ProfileOut)
def get_profile(user: User = Depends(get_current_user)) -> ProfileOut:
    return ProfileOut(**dump_profile(user))


@router.patch("", response_model=ProfileOut)
def update_profile(
    payload: ProfilePatch,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ProfileOut:
    data = payload.model_dump(exclude_unset=True)
    if "display_name" in data:
        display_name = (data["display_name"] or "").strip()
        if not display_name:
            raise HTTPException(status_code=400, detail="Укажите имя")
        user.display_name = display_name
    if "role" in data:
        role = (data["role"] or "").strip()
        if not role:
            raise HTTPException(status_code=400, detail="Укажите роль")
        user.role = role
    if "city" in data:
        city = (data["city"] or "").strip()
        if not city:
            raise HTTPException(status_code=400, detail="Укажите город")
        user.city = city
    if "notifications_enabled" in data:
        user.notifications_enabled = data["notifications_enabled"]
    db.commit()
    db.refresh(user)
    return ProfileOut(**dump_profile(user))

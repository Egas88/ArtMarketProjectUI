from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import User
from app.presenters import dump_profile
from app.schemas import LoginRequest, ProfileOut, RegisterRequest, TokenOut
from app.security import create_access_token, hash_password, verify_password

router = APIRouter()


def _check_new_password(password: str) -> None:
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="Пароль минимум 4 символа")
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Пароль слишком длинный")


def _check_username(username: str) -> str:
    username = username.strip()
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Имя должно быть от 3 символов")
    if len(username) > 64:
        raise HTTPException(status_code=400, detail="Имя должно быть не длиннее 64 символов")
    return username


def _token_response(user: User) -> TokenOut:
    return TokenOut(access_token=create_access_token(user.id), user=ProfileOut(**dump_profile(user)))


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenOut:
    username = _check_username(payload.username)
    _check_new_password(payload.password)
    if db.scalar(select(User).where(User.username == username)) is not None:
        raise HTTPException(status_code=409, detail="Такой пользователь уже существует")

    user = User(
        username=username,
        password_hash=hash_password(payload.password),
        display_name=username,
        role="Художник / Мастер",
        city="Санкт-Петербург",
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Такой пользователь уже существует") from None
    db.refresh(user)
    return _token_response(user)


@router.post("/login", response_model=TokenOut)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenOut:
    username = payload.username.strip()
    user = db.scalar(select(User).where(User.username == username))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверное имя или пароль")
    return _token_response(user)


@router.get("/me", response_model=ProfileOut)
def me(user: User = Depends(get_current_user)) -> ProfileOut:
    return ProfileOut(**dump_profile(user))

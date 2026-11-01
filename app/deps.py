from collections.abc import Generator

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User
from app.security import user_id_from_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _user_from_credentials(
    db: Session,
    credentials: HTTPAuthorizationCredentials | None,
) -> User | None:
    if credentials is None:
        return None
    user_id = user_id_from_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    return user


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
    user = _user_from_credentials(db, credentials)
    if user is None:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    return user


def get_optional_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User | None:
    return _user_from_credentials(db, credentials)

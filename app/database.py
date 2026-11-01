import time

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def wait_for_db(retries: int = 30, delay: float = 1.0) -> None:
    last_error: OperationalError | None = None
    for _ in range(retries):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return
        except OperationalError as exc:
            last_error = exc
            time.sleep(delay)
    raise RuntimeError("База данных недоступна") from last_error

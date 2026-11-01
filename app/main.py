import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.config import settings
from app.database import Base, SessionLocal, engine, wait_for_db
from app.deps import get_db
from app.routers import applications, auth, favorites, markets, profile, resumes
from app.seed import seed_if_empty

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_db()
    Base.metadata.create_all(bind=engine)
    if settings.seed_on_startup:
        with SessionLocal() as db:
            created = seed_if_empty(db)
        logger.info("Тестовые данные записаны" if created else "В базе уже есть маркеты, наполнение пропущено")
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Арт-Маркет API",
        version="1.0.0",
        summary="Бэкенд путеводителя по локальным маркетам и ярмаркам.",
        lifespan=lifespan,
    )
    origins = [item.strip() for item in settings.cors_origins.split(",") if item.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(markets.router, prefix="/api/markets", tags=["markets"])
    app.include_router(favorites.router, prefix="/api/favorites", tags=["favorites"])
    app.include_router(resumes.router, prefix="/api/resumes", tags=["resumes"])
    app.include_router(applications.router, prefix="/api/applications", tags=["applications"])
    app.include_router(profile.router, prefix="/api/me", tags=["profile"])

    @app.get("/")
    def root() -> dict[str, str]:
        return {"service": "artmarket", "docs": "/docs"}

    @app.get("/api/health")
    def health(db: Session = Depends(get_db)) -> dict[str, str]:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}

    return app


app = create_app()

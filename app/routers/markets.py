from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import Text, cast, func, or_, select
from sqlalchemy.orm import Session

from app.deps import get_db, get_optional_user
from app.models import Market, User
from app.presenters import dump_market
from app.queries import applications_for, favorite_ids_for, get_market_or_404
from app.schemas import MarketOut

router = APIRouter()


def _like(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


@router.get("", response_model=list[MarketOut])
def list_markets(
    q: str | None = None,
    city: str | None = None,
    upcoming: bool = False,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
) -> list[MarketOut]:
    statement = select(Market)
    if q and q.strip():
        pattern = _like(q.strip())
        statement = statement.where(
            or_(
                Market.title.ilike(pattern, escape="\\"),
                Market.description.ilike(pattern, escape="\\"),
                Market.city.ilike(pattern, escape="\\"),
                Market.venue_name.ilike(pattern, escape="\\"),
                Market.address.ilike(pattern, escape="\\"),
                cast(Market.tags, Text).ilike(pattern, escape="\\"),
            )
        )
    if city and city.strip():
        statement = statement.where(func.lower(Market.city) == city.strip().lower())
    if upcoming:
        statement = statement.where(Market.end_date >= date.today())

    statement = statement.order_by(Market.start_date, Market.id).offset(offset).limit(limit)
    markets = db.scalars(statement).all()
    favorite_ids = favorite_ids_for(db, user)
    applications = applications_for(db, user)
    return [
        MarketOut(**dump_market(market, favorite_ids=favorite_ids, applications=applications))
        for market in markets
    ]


@router.get("/{market_id}", response_model=MarketOut)
def get_market(
    market_id: str,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
) -> MarketOut:
    market = get_market_or_404(db, market_id)
    return MarketOut(
        **dump_market(
            market,
            favorite_ids=favorite_ids_for(db, user),
            applications=applications_for(db, user),
        )
    )

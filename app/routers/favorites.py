from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import Favorite, User
from app.presenters import dump_market
from app.queries import applications_for, favorite_ids_for, get_market_or_404
from app.schemas import MarketOut

router = APIRouter()


def _market_out(db: Session, user: User, market_id: str) -> MarketOut:
    market = get_market_or_404(db, market_id)
    return MarketOut(
        **dump_market(
            market,
            favorite_ids=favorite_ids_for(db, user),
            applications=applications_for(db, user),
        )
    )


@router.get("", response_model=list[MarketOut])
def list_favorites(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[MarketOut]:
    favorites = db.scalars(
        select(Favorite).where(Favorite.user_id == user.id).order_by(Favorite.created_at, Favorite.market_id)
    ).all()
    applications = applications_for(db, user)
    favorite_ids = {item.market_id for item in favorites}
    return [
        MarketOut(**dump_market(item.market, favorite_ids=favorite_ids, applications=applications))
        for item in favorites
    ]


@router.post("/{market_id}", response_model=MarketOut)
def add_favorite(
    market_id: str,
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MarketOut:
    get_market_or_404(db, market_id)
    existing = db.get(Favorite, {"user_id": user.id, "market_id": market_id})
    if existing is None:
        db.add(Favorite(user_id=user.id, market_id=market_id))
        db.commit()
        response.status_code = 201
    else:
        response.status_code = 200
    return _market_out(db, user, market_id)


@router.delete("/{market_id}", status_code=204)
def remove_favorite(
    market_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    get_market_or_404(db, market_id)
    favorite = db.get(Favorite, {"user_id": user.id, "market_id": market_id})
    if favorite is not None:
        db.delete(favorite)
        db.commit()

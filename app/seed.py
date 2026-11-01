from datetime import date, time

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Application, Market, Organizer, Resume, User
from app.security import hash_password

ART_DVOR_DESCRIPTION = (
    "Уютный петербургский маркет во дворе старинного особняка. "
    "Место встречи локальных художников, гончаров и дизайнеров одежды. "
    "Вас ждут уникальная керамика ручной работы, оригинальные постеры, "
    "крафтовые свечи, а также виниловый корнер и зона апсайклинга."
)


def seed_if_empty(db: Session) -> bool:
    existing = db.scalar(select(func.count()).select_from(Market))
    if existing:
        return False

    organizer = Organizer(name="Студия «Арт-Союз»", role="Организатор")
    markets = [
        Market(
            id="tsvetochny",
            title="Маркет «Цветочный»",
            description="Двухдневный маркет цветов, керамики и декора.",
            city="Санкт-Петербург",
            image="Цветочный рынок",
            tags=["Цветы", "Керамика", "Декор"],
            start_date=date(2026, 5, 25),
            end_date=date(2026, 5, 26),
            opens_at=time(12, 0),
            closes_at=time(21, 0),
        ),
        Market(
            id="vesna",
            title="Ярмарка «Весна»",
            description="Ярмарка хендмейда: одежда, свечи и работы локальных мастеров.",
            city="Санкт-Петербург",
            image="Ярмарка одежды",
            tags=["Хендмейд", "Одежда", "Свечи"],
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 2),
            opens_at=time(11, 0),
            closes_at=time(20, 0),
        ),
        Market(
            id="art-dvor",
            title="Маркет «Арт-Двор»",
            description=ART_DVOR_DESCRIPTION,
            city="Санкт-Петербург",
            venue_name="Двор Особняка Слепцова",
            address="ул. Большая Конюшенная, 9",
            image="Арт-двор",
            tags=["Картины", "Посуда", "Винил"],
            start_date=date(2026, 6, 8),
            end_date=date(2026, 6, 8),
            opens_at=time(12, 0),
            closes_at=time(22, 0),
            # Приблизительные координаты адреса из макета, для экрана карты.
            latitude=59.9398,
            longitude=30.3235,
            organizer=organizer,
        ),
    ]
    user = User(
        username="test",
        password_hash=hash_password("1111"),
        display_name="Test User",
        role="Художник / Мастер",
        city="Санкт-Петербург",
        notifications_enabled=True,
    )
    garden = Resume(
        user=user,
        nickname="Терракотовый сад",
        real_name="Мария Савельева",
        about=(
            "Занимаюсь ручной лепкой из глины уже более 5 лет. "
            "Каждое изделие уникально и наполнено природным теплом."
        ),
        telegram="@terracotta_garden",
        phone="+7 (911) 234-56-78",
        email="maria@artmarket.ru",
        photos=[None, None, None],
    )
    ceramics = Resume(
        user=user,
        nickname="Для керамики",
        real_name="Мария Савельева",
        about="Специализация на посуде и декоре.",
        photos=[None, None, None, None, None],
    )
    applications = [
        Application(user=user, market=markets[2], resume=garden, status="participating", message=""),
        Application(user=user, market=markets[0], resume=garden, status="pending", message=""),
        Application(user=user, market=markets[1], resume=ceramics, status="rejected", message=""),
    ]
    db.add_all([organizer, *markets, user, garden, ceramics, *applications])
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return False
    return True

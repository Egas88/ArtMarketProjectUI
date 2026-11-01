from app.models import Market

MONTHS = (
    "",
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
)

STATUS_LABELS = {
    "participating": "Вы участвуете",
    "pending": "Заявка на рассмотрении",
    "rejected": "Ваше участие отклонено",
}


def format_meta(market: Market, *, with_pin: bool = False) -> str:
    if market.start_date == market.end_date:
        dates = f"{market.start_date.day} {MONTHS[market.start_date.month]}"
    elif market.start_date.month == market.end_date.month and market.start_date.year == market.end_date.year:
        dates = f"{market.start_date.day}–{market.end_date.day} {MONTHS[market.start_date.month]}"
    else:
        start = f"{market.start_date.day} {MONTHS[market.start_date.month]}"
        end = f"{market.end_date.day} {MONTHS[market.end_date.month]}"
        dates = f"{start} – {end}"

    hours = f"{market.opens_at.strftime('%H:%M')}–{market.closes_at.strftime('%H:%M')}"
    place = f"📍 {market.city}" if with_pin else market.city
    return f"📅 {dates}, {hours} · {place}"


def cabinet_name(user) -> str:
    if user.resumes:
        return user.resumes[0].nickname
    return user.display_name or user.username

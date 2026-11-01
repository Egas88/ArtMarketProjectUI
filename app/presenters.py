from app.formatting import STATUS_LABELS, cabinet_name, format_meta
from app.models import Application, Market, Resume, User


def dump_resume(resume: Resume) -> dict:
    photos = list(resume.photos or [])
    return {
        "id": resume.id,
        "nickname": resume.nickname,
        "real_name": resume.real_name,
        "about": resume.about,
        "telegram": resume.telegram,
        "phone": resume.phone,
        "email": resume.email,
        "photos": photos,
        "photo_count": len(photos),
    }


def dump_profile(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "role": user.role,
        "city": user.city,
        "notifications_enabled": user.notifications_enabled,
        "cabinet_name": cabinet_name(user),
        "resumes_count": len(user.resumes),
    }


def dump_market(
    market: Market,
    *,
    favorite_ids: set[str],
    applications: dict[str, Application],
) -> dict:
    application = applications.get(market.id)
    organizer = None
    if market.organizer is not None:
        organizer = {
            "id": market.organizer.id,
            "name": market.organizer.name,
            "role": market.organizer.role,
        }
    brief = None
    if application is not None:
        brief = {
            "id": application.id,
            "status": application.status,
            "status_label": STATUS_LABELS[application.status],
        }
    return {
        "id": market.id,
        "title": market.title,
        "city": market.city,
        "venue_name": market.venue_name,
        "address": market.address,
        "description": market.description,
        "image": market.image,
        "tags": list(market.tags or []),
        "start_date": market.start_date.isoformat(),
        "end_date": market.end_date.isoformat(),
        "opens_at": market.opens_at.strftime("%H:%M"),
        "closes_at": market.closes_at.strftime("%H:%M"),
        "meta": format_meta(market),
        "detail_meta": format_meta(market, with_pin=True),
        "latitude": market.latitude,
        "longitude": market.longitude,
        "organizer": organizer,
        "is_favorite": market.id in favorite_ids,
        "my_application": brief,
    }


def dump_application(
    application: Application,
    *,
    favorite_ids: set[str],
    applications: dict[str, Application],
) -> dict:
    return {
        "id": application.id,
        "status": application.status,
        "status_label": STATUS_LABELS[application.status],
        "message": application.message,
        "resume_id": application.resume_id,
        "created_at": application.created_at,
        "market": dump_market(
            application.market,
            favorite_ids=favorite_ids,
            applications=applications,
        ),
    }

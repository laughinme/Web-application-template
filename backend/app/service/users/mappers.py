from app.db.models import User
from app.domain.users import UserProfile
from app.service.ports import PublicUrls


def to_profile(user: User, urls: PublicUrls) -> UserProfile:
    return UserProfile(
        id=user.id,
        email=user.email,
        username=user.username,
        bio=user.bio,
        avatar_key=user.avatar_key,
        avatar_url=urls.public_url(user.avatar_key) if user.avatar_key else None,
        role=user.role,
        is_onboarded=user.is_onboarded,
        is_banned=user.banned_at is not None,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )

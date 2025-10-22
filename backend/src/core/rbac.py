from uuid import UUID

PERMISSIONS_CACHE_TTL_SECONDS = 900


def permissions_cache_key(user_id: UUID | str, version: int) -> str:
    return f"auth:perm:{user_id}:v{version}"

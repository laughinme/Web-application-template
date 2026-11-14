from datetime import timedelta

_MAX_RETRY_DELAY = timedelta(hours=1)


def retry_delay(attempt: int) -> timedelta:
    """Exponential backoff: 2 s, 4 s, 8 s ... capped at one hour."""
    return min(timedelta(seconds=2**attempt), _MAX_RETRY_DELAY)

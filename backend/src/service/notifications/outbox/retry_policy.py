from datetime import UTC, datetime, timedelta


_BACKOFF_SECONDS = (10, 30, 60, 120, 300, 600, 1800)


def compute_next_attempt(attempt_number: int) -> datetime:
    index = max(0, min(attempt_number - 1, len(_BACKOFF_SECONDS) - 1))
    return datetime.now(UTC) + timedelta(seconds=_BACKOFF_SECONDS[index])

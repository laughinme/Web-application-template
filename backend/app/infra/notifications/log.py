import logging

logger = logging.getLogger(__name__)


class LogNotifier:
    """Default adapter for `Notifier`: writes to the log. Used in dev, tests and as a fallback."""

    async def send(self, text: str) -> None:
        logger.info("notification: %s", text)

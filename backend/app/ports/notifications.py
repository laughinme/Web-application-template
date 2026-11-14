from typing import Protocol


class Notifier(Protocol):
    """A message to the team (new user, failed job). Adapters: log, Telegram."""

    async def send(self, text: str) -> None: ...

from app.domain.outbox import Topic
from app.infra.notifications import LogNotifier
from app.service.outbox import build_handlers
from tests.factories import RecordingNotifier


class NullStorage:
    async def delete(self, key: str) -> None:
        return None


def test_every_topic_has_a_handler() -> None:
    # An event nobody handles goes straight to `dead`; catch the missing wiring here.
    assert set(build_handlers(LogNotifier(), NullStorage())) == set(Topic)


async def test_registration_handler_notifies() -> None:
    notifier = RecordingNotifier()

    await build_handlers(notifier, NullStorage())[Topic.USER_REGISTERED]({"email": "a@b.c"})

    assert notifier.messages == ["New user registered: a@b.c"]

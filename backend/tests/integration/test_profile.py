from collections.abc import Awaitable, Callable

import httpx
from httpx import AsyncClient

from app.infra.storage import ObjectStorage
from tests.factories import Account

ME = "/api/v1/users/me"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


async def test_patch_sets_and_clears_fields(user: Account, client: AsyncClient) -> None:
    updated = await client.patch(
        ME, json={"username": "trinity", "bio": "hi"}, headers=user.headers
    )
    assert updated.status_code == 200
    assert (updated.json()["username"], updated.json()["bio"]) == ("trinity", "hi")

    cleared = await client.patch(ME, json={"bio": None}, headers=user.headers)
    assert cleared.json()["bio"] is None
    assert cleared.json()["username"] == "trinity"


async def test_patch_rejects_unknown_fields(user: Account, client: AsyncClient) -> None:
    response = await client.patch(ME, json={"role": "admin"}, headers=user.headers)

    assert response.status_code == 422
    assert response.json()["error_code"] == "REQUEST_VALIDATION_ERROR"


async def _upload_avatar(client: AsyncClient, user: Account) -> dict[str, str]:
    presign = await client.post(
        f"{ME}/avatar/presign", json={"content_type": "image/png"}, headers=user.headers
    )
    assert presign.status_code == 200
    data: dict[str, str] = presign.json()
    async with httpx.AsyncClient() as storage_client:
        upload = await storage_client.put(
            data["upload_url"], content=PNG, headers={"Content-Type": "image/png"}
        )
    assert upload.status_code == 200
    return data


async def test_avatar_upload_replace_and_cleanup(
    user: Account,
    client: AsyncClient,
    storage: ObjectStorage,
    run_outbox: Callable[[], Awaitable[int]],
) -> None:
    first = await _upload_avatar(client, user)
    confirmed = await client.post(
        f"{ME}/avatar/confirm", json={"object_key": first["object_key"]}, headers=user.headers
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["avatar_url"] == first["public_url"]
    async with httpx.AsyncClient() as anonymous:
        assert (await anonymous.get(first["public_url"])).content == PNG

    second = await _upload_avatar(client, user)
    await client.post(
        f"{ME}/avatar/confirm", json={"object_key": second["object_key"]}, headers=user.headers
    )

    # The old file is removed by the worker after commit, not inside the request.
    assert await storage.stat(first["object_key"]) is not None
    await run_outbox()
    assert await storage.stat(first["object_key"]) is None
    assert await storage.stat(second["object_key"]) is not None


async def test_confirm_without_upload_is_409(user: Account, client: AsyncClient) -> None:
    presign = await client.post(
        f"{ME}/avatar/presign", json={"content_type": "image/webp"}, headers=user.headers
    )
    response = await client.post(
        f"{ME}/avatar/confirm",
        json={"object_key": presign.json()["object_key"]},
        headers=user.headers,
    )

    assert response.status_code == 409
    assert response.json()["error_code"] == "AVATAR_NOT_UPLOADED"


async def test_cannot_claim_another_users_file(
    user: Account, admin: Account, client: AsyncClient
) -> None:
    theirs = await _upload_avatar(client, admin)

    response = await client.post(
        f"{ME}/avatar/confirm", json={"object_key": theirs["object_key"]}, headers=user.headers
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "AVATAR_KEY_INVALID"

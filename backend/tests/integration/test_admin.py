from httpx import AsyncClient

from tests.factories import Account, register

USERS = "/api/v1/admin/users"


async def test_members_cannot_use_admin_endpoints(user: Account, client: AsyncClient) -> None:
    response = await client.get(USERS, headers=user.headers)

    assert response.status_code == 403
    assert response.json()["error_code"] == "FORBIDDEN"


async def test_list_users_pages_with_cursor(admin: Account, client: AsyncClient) -> None:
    for index in range(4):
        await register(client, email=f"page{index}@example.com")

    first = await client.get(USERS, params={"limit": 3}, headers=admin.headers)
    second = await client.get(
        USERS, params={"limit": 3, "cursor": first.json()["next_cursor"]}, headers=admin.headers
    )

    first_ids = [item["id"] for item in first.json()["items"]]
    second_ids = [item["id"] for item in second.json()["items"]]
    assert len(first_ids) == 3
    assert len(second_ids) == 2  # 4 members + the admin
    assert not set(first_ids) & set(second_ids)
    assert second.json()["next_cursor"] is None


async def test_search_escapes_like_wildcards(admin: Account, client: AsyncClient) -> None:
    await register(client, email="plain@example.com")

    response = await client.get(USERS, params={"search": "%"}, headers=admin.headers)

    assert response.json()["items"] == []


async def test_ban_kills_sessions_and_blocks_login(
    admin: Account, user: Account, client: AsyncClient
) -> None:
    banned = await client.post(f"{USERS}/{user.id}/ban", headers=admin.headers)
    assert banned.status_code == 200
    assert banned.json()["banned"] is True

    me = await client.get("/api/v1/users/me", headers=user.headers)
    assert me.status_code == 401
    login = await client.post(
        "/api/v1/auth/login", json={"email": user.email, "password": user.password}
    )
    assert login.status_code == 403
    assert login.json()["error_code"] == "ACCOUNT_BANNED"

    unbanned = await client.delete(f"{USERS}/{user.id}/ban", headers=admin.headers)
    assert unbanned.json()["banned"] is False


async def test_admin_cannot_ban_self_or_other_admins(
    admin: Account, user: Account, client: AsyncClient
) -> None:
    self_ban = await client.post(f"{USERS}/{admin.id}/ban", headers=admin.headers)
    assert self_ban.json()["error_code"] == "SELF_MODERATION"

    await client.put(f"{USERS}/{user.id}/role", json={"role": "admin"}, headers=admin.headers)
    other_admin = await client.post(f"{USERS}/{user.id}/ban", headers=admin.headers)
    assert other_admin.status_code == 403
    assert other_admin.json()["error_code"] == "ADMIN_PROTECTED"


async def test_role_change_applies_to_the_next_request(
    admin: Account, user: Account, client: AsyncClient
) -> None:
    assert (await client.get(USERS, headers=user.headers)).status_code == 403

    promoted = await client.put(
        f"{USERS}/{user.id}/role", json={"role": "admin"}, headers=admin.headers
    )
    assert promoted.json()["role"] == "admin"

    assert (await client.get(USERS, headers=user.headers)).status_code == 200


async def test_unknown_user_is_404(admin: Account, client: AsyncClient) -> None:
    response = await client.post(
        f"{USERS}/00000000-0000-0000-0000-000000000000/ban", headers=admin.headers
    )

    assert response.status_code == 404
    assert response.json()["error_code"] == "USER_NOT_FOUND"


async def test_stats(admin: Account, user: Account, client: AsyncClient) -> None:
    summary = await client.get("/api/v1/admin/stats/users", headers=admin.headers)
    daily = await client.get(
        "/api/v1/admin/stats/registrations", params={"days": 7}, headers=admin.headers
    )

    assert summary.json()["total"] == 2
    assert summary.json()["registered_last_24h"] == 2
    assert sum(row["count"] for row in daily.json()) == 2

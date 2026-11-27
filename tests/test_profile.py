"""Тесты просмотра и редактирования профиля."""

from __future__ import annotations

import httpx
import pytest

pytestmark = pytest.mark.asyncio


async def test_profile_requires_authorization(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/profile")

    assert response.status_code == 401


async def test_profile_rejects_invalid_token(client: httpx.AsyncClient) -> None:
    response = await client.get(
        "/api/profile",
        headers={"Authorization": "Bearer deadbeef"},
    )

    assert response.status_code == 401


async def test_profile_rejects_non_bearer_scheme(
    client: httpx.AsyncClient, auth_headers: dict[str, str]
) -> None:
    """Валидный токен, но неверная схема авторизации, не должен давать доступ."""
    token = auth_headers["Authorization"].split()[-1]

    response = await client.get(
        "/api/profile",
        headers={"Authorization": f"Basic {token}"},
    )

    assert response.status_code == 401


async def test_get_profile_returns_registered_data(
    client: httpx.AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.get("/api/profile", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {
        "username": "testuser",
        "email": "testuser@example.com",
        "name": "Test User",
    }


async def test_update_profile_changes_email_and_name(
    client: httpx.AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.put(
        "/api/profile",
        headers=auth_headers,
        json={"email": "testuser2@example.com", "name": "Test User 2"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "username": "testuser",
        "email": "testuser2@example.com",
        "name": "Test User 2",
    }


async def test_update_profile_is_persisted(
    client: httpx.AsyncClient, auth_headers: dict[str, str]
) -> None:
    await client.put(
        "/api/profile",
        headers=auth_headers,
        json={"email": "testuser3@example.com"},
    )

    response = await client.get("/api/profile", headers=auth_headers)

    assert response.json()["email"] == "testuser3@example.com"


async def test_update_profile_rejects_empty_body(
    client: httpx.AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.put("/api/profile", headers=auth_headers, json={})

    assert response.status_code == 422


async def test_update_profile_requires_authorization(client: httpx.AsyncClient) -> None:
    response = await client.put("/api/profile", json={"name": "Hacker"})

    assert response.status_code == 401

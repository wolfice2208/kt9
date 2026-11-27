"""Тесты регистрации и аутентификации."""

from __future__ import annotations

import httpx
import pytest

from tests.conftest import REGISTER_PAYLOAD

pytestmark = pytest.mark.asyncio


async def test_register_returns_201_and_access_token(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/register", json=REGISTER_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


async def test_register_rejects_duplicate_username(client: httpx.AsyncClient) -> None:
    await client.post("/api/register", json=REGISTER_PAYLOAD)

    response = await client.post("/api/register", json=REGISTER_PAYLOAD)

    assert response.status_code == 409


async def test_register_rejects_invalid_email(client: httpx.AsyncClient) -> None:
    payload = {**REGISTER_PAYLOAD, "email": "not-an-email"}

    response = await client.post("/api/register", json=payload)

    assert response.status_code == 422


async def test_register_rejects_too_short_password(client: httpx.AsyncClient) -> None:
    payload = {**REGISTER_PAYLOAD, "password": "1"}

    response = await client.post("/api/register", json=payload)

    assert response.status_code == 422


async def test_login_returns_access_token(client: httpx.AsyncClient) -> None:
    await client.post("/api/register", json=REGISTER_PAYLOAD)

    response = await client.post(
        "/api/login",
        json={"username": "testuser", "password": "testpass"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_login_rejects_wrong_password(client: httpx.AsyncClient) -> None:
    await client.post("/api/register", json=REGISTER_PAYLOAD)

    response = await client.post(
        "/api/login",
        json={"username": "testuser", "password": "wrong-password"},
    )

    assert response.status_code == 401


async def test_login_rejects_unknown_user(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/api/login",
        json={"username": "ghost", "password": "testpass"},
    )

    assert response.status_code == 401

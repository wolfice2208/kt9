from __future__ import annotations

import httpx
import pytest_asyncio

from app import main

REGISTER_PAYLOAD = {
    "username": "testuser",
    "password": "testpass",
    "email": "testuser@example.com",
    "name": "Test User",
}


@pytest_asyncio.fixture
async def client() -> httpx.AsyncClient:
    """Асинхронный HTTP-клиент поверх ASGI-приложения, изолированный по состоянию."""
    main.reset_state()
    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client


@pytest_asyncio.fixture
async def auth_headers(client: httpx.AsyncClient) -> dict[str, str]:
    """Заголовок Authorization для уже зарегистрированного пользователя."""
    response = await client.post("/api/register", json=REGISTER_PAYLOAD)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

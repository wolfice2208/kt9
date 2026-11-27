"""User Profile API — веб-приложение, которое тестируется в рамках задания.

Учебная реализация: in-memory хранилище, токены без срока жизни.
Спецификация: регистрация, вход, просмотр и редактирование профиля.
"""

from __future__ import annotations

import hashlib
import secrets
import uuid

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="User Profile API", version="1.0.0")

# username -> {"password_hash": str, "salt": str, "email": str, "name": str}
_users: dict[str, dict[str, str]] = {}
# token -> username
_tokens: dict[str, str] = {}


def reset_state() -> None:
    """Очистка состояния между тестами."""
    _users.clear()
    _tokens.clear()


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str
    name: str = ""


class LoginRequest(BaseModel):
    username: str
    password: str


class ProfileUpdate(BaseModel):
    email: str | None = None
    name: str | None = None


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def _issue_token(username: str) -> str:
    token = uuid.uuid4().hex
    _tokens[token] = username
    return token


def _current_user(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
        )
    token = authorization.split()[-1]
    username = _tokens.get(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return username


def _public_profile(username: str) -> dict[str, str]:
    user = _users[username]
    return {"username": username, "email": user["email"], "name": user["name"]}


@app.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest) -> dict[str, str]:
    if payload.username in _users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is already taken",
        )
    salt = secrets.token_hex(16)
    _users[payload.username] = {
        "password_hash": _hash_password(payload.password, salt),
        "salt": salt,
        "email": payload.email,
        "name": payload.name,
    }
    return {"access_token": _issue_token(payload.username), "token_type": "bearer"}


@app.post("/api/login")
async def login(payload: LoginRequest) -> dict[str, str]:
    user = _users.get(payload.username)
    if not user or user["password_hash"] != _hash_password(
        payload.password, user["salt"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return {"access_token": _issue_token(payload.username), "token_type": "bearer"}


@app.get("/api/profile")
async def get_profile(authorization: str | None = Header(default=None)) -> dict[str, str]:
    return _public_profile(_current_user(authorization))


@app.put("/api/profile")
async def update_profile(
    payload: ProfileUpdate,
    authorization: str | None = Header(default=None),
) -> dict[str, str]:
    username = _current_user(authorization)
    if payload.email is not None:
        _users[username]["email"] = payload.email
    if payload.name is not None:
        _users[username]["name"] = payload.name
    return _public_profile(username)

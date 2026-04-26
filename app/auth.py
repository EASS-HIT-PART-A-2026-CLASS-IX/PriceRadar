from __future__ import annotations

import base64
import hashlib
import hmac
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlmodel import Session

from app.config import get_settings
from app.database import get_session
from app.models import AppUser, UserRole
from app.repositories import UserRepository

PBKDF2_ITERATIONS = 390_000
bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(slots=True)
class AuthenticatedUser:
    user: AppUser
    scopes: set[str]


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return "pbkdf2_sha256${}${}${}".format(
        PBKDF2_ITERATIONS,
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, password_hash: str) -> bool:
    algorithm, iterations_text, salt_text, digest_text = password_hash.split("$", maxsplit=3)
    if algorithm != "pbkdf2_sha256":
        return False
    salt = base64.urlsafe_b64decode(salt_text.encode("ascii"))
    expected = base64.urlsafe_b64decode(digest_text.encode("ascii"))
    iterations = int(iterations_text)
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(actual, expected)


def create_access_token(*, subject: str, role: UserRole, scopes: list[str], expires_delta: timedelta) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "role": role.value,
        "scopes": scopes,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, object]:
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> AuthenticatedUser:
    if credentials is None:
        raise _unauthorized("Missing bearer token")

    try:
        payload = decode_access_token(credentials.credentials)
    except InvalidTokenError as exc:
        raise _unauthorized("Invalid or expired token") from exc

    subject = payload.get("sub")
    if not isinstance(subject, str):
        raise _unauthorized("Invalid token subject")

    user = UserRepository(session).get_by_email(subject)
    if user is None or not user.is_active:
        raise _unauthorized("User is inactive or missing")

    scopes = payload.get("scopes", [])
    if not isinstance(scopes, list):
        raise _unauthorized("Invalid token scopes")

    return AuthenticatedUser(user=user, scopes={scope for scope in scopes if isinstance(scope, str)})


def require_scope(scope: str):
    def dependency(current: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if scope not in current.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required scope: {scope}",
            )
        return current

    return dependency


def require_role(role: UserRole):
    def dependency(current: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if current.user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {role.value} is required",
            )
        return current

    return dependency

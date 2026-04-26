from __future__ import annotations

from sqlmodel import Session

from app.auth import hash_password
from app.config import get_settings
from app.models import AppUser, UserRole
from app.repositories import UserRepository


def ensure_demo_users(session: Session) -> None:
    settings = get_settings()
    users = UserRepository(session)
    demo_users = [
        AppUser(
            email=settings.demo_admin_email,
            full_name=settings.demo_admin_name,
            password_hash=hash_password(settings.demo_admin_password),
            role=UserRole.admin,
            is_active=True,
        ),
        AppUser(
            email=settings.demo_analyst_email,
            full_name=settings.demo_analyst_name,
            password_hash=hash_password(settings.demo_analyst_password),
            role=UserRole.analyst,
            is_active=True,
        ),
    ]
    existing = {user.email for user in users.list()}
    for user in demo_users:
        if user.email not in existing:
            users.create(user)

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.accounts.application.account_recovery import (  # noqa: E402
    AccountRecoveryUseCase,
)


@dataclass
class _Token:
    id: int
    usuario: object
    tipo: str
    expires_at: datetime
    used_at: datetime | None = None
    status: str = "pendente"
    Status = SimpleNamespace(PENDENTE="pendente")


class _Repo:
    class _Types:
        EMAIL_CONFIRMATION = "email_confirmation"
        PASSWORD_RESET = "password_reset"

    def __init__(self):
        self.users = {}
        self.tokens = {}
        self.events = []
        self.invalidations = []
        self.saved_passwords = {}

    def find_user_by_email(self, *, email: str):
        return self.users.get(email.lower())

    def find_token_by_code(self, *, code: str, token_type: str):
        token = self.tokens.get((code, token_type))
        return token

    def invalidate_open_tokens(self, *, user, token_type: str, now) -> None:
        self.invalidations.append((user.id, token_type))

    def create_token(self, *, user, token_type: str, expires_at, ip: str | None):
        token = _Token(
            id=len(self.tokens) + 1,
            usuario=user,
            tipo=token_type,
            expires_at=expires_at,
        )
        self.tokens[(f"new-{token.id}", token_type)] = token
        return token

    def create_security_event(self, *, user, event_name: str, ip: str | None) -> None:
        self.events.append((user.id, event_name, ip))

    def activate_user_email(self, *, user) -> None:
        user.is_active = True
        user.email_confirmed = True

    def mark_token_used(self, *, token) -> None:
        token.used_at = datetime.now(timezone.utc)

    def mark_token_confirmed(self, *, token) -> None:
        token.status = "confirmado"

    def save_user_password(self, *, user, raw_password: str) -> None:
        self.saved_passwords[user.id] = raw_password

    def validate_password(self, *, user, raw_password: str) -> list[str]:
        if len(raw_password) < 8:
            return ["Senha muito curta."]
        return []

    def clear_login_failures(self, *, user) -> None:
        return None

    def get_token_types(self) -> object:
        return self._Types


class _Notifier:
    def __init__(self):
        self.sent_confirmation = []
        self.sent_reset = []

    def send_confirmation_email(self, *, token_id: int) -> None:
        self.sent_confirmation.append(token_id)

    def send_password_reset_email(self, *, token_id: int) -> None:
        self.sent_reset.append(token_id)


def _now():
    return datetime(2026, 3, 10, 12, 0, tzinfo=timezone.utc)


def test_confirm_email_success():
    repo = _Repo()
    notifier = _Notifier()
    user = SimpleNamespace(id=1, is_active=False, email_confirmed=False)
    token = _Token(
        id=10,
        usuario=user,
        tipo=repo._Types.EMAIL_CONFIRMATION,
        expires_at=_now() + timedelta(hours=1),
    )
    repo.tokens[("ok", repo._Types.EMAIL_CONFIRMATION)] = token
    use_case = AccountRecoveryUseCase(repository=repo, notifier=notifier, now=_now)

    result = use_case.confirm_email_token(code="ok", ip="127.0.0.1")

    assert result.status == "success"
    assert user.is_active is True
    assert user.email_confirmed is True


def test_request_password_reset_ignores_unknown_email():
    repo = _Repo()
    notifier = _Notifier()
    use_case = AccountRecoveryUseCase(repository=repo, notifier=notifier, now=_now)

    result = use_case.request_password_reset(email="missing@example.com", ip=None)

    assert result.status == "ignored"
    assert notifier.sent_reset == []


def test_reset_password_invalid_password():
    repo = _Repo()
    notifier = _Notifier()
    user = SimpleNamespace(id=2, is_active=True, email_confirmed=True)
    token = _Token(
        id=11,
        usuario=user,
        tipo=repo._Types.PASSWORD_RESET,
        expires_at=_now() + timedelta(hours=1),
    )
    repo.tokens[("tok", repo._Types.PASSWORD_RESET)] = token
    use_case = AccountRecoveryUseCase(repository=repo, notifier=notifier, now=_now)

    result = use_case.reset_password(code="tok", raw_password="123", ip=None)

    assert result.status == "invalid_password"
    assert result.errors == ["Senha muito curta."]

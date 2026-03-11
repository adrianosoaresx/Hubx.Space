import os
from datetime import timedelta
from types import SimpleNamespace

import django
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.accounts.application.account_delete_cancellation import (  # noqa: E402
    AccountDeleteCancellationUseCase,
)


class _FakeRepository:
    def __init__(self, token=None):
        self.token = token
        self.reactivate_calls = []
        self.lookup_codes = []

    def find_cancel_delete_token(self, *, code: str):
        self.lookup_codes.append(code)
        return self.token

    def reactivate_user_from_cancel_token(self, *, token, ip: str | None):
        self.reactivate_calls.append({"token": token, "ip": ip})
        return getattr(token, "usuario", None)


def test_cancel_delete_use_case_missing_token():
    use_case = AccountDeleteCancellationUseCase(
        repository=_FakeRepository(),
        now=timezone.now,
    )

    result = use_case.execute(code=None, ip="127.0.0.1")

    assert result.status == "missing_token"
    assert result.user is None


def test_cancel_delete_use_case_invalid_or_expired_token():
    expired_token = SimpleNamespace(
        expires_at=timezone.now() - timedelta(minutes=1),
        used_at=None,
        usuario=SimpleNamespace(id=1),
    )
    repository = _FakeRepository(token=expired_token)
    use_case = AccountDeleteCancellationUseCase(
        repository=repository,
        now=timezone.now,
    )

    result = use_case.execute(code="token-expirado", ip="127.0.0.1")

    assert result.status == "invalid_or_expired"
    assert result.user is None
    assert repository.reactivate_calls == []


def test_cancel_delete_use_case_success():
    user = SimpleNamespace(id=10)
    token = SimpleNamespace(
        expires_at=timezone.now() + timedelta(minutes=30),
        used_at=None,
        usuario=user,
    )
    repository = _FakeRepository(token=token)
    use_case = AccountDeleteCancellationUseCase(
        repository=repository,
        now=timezone.now,
    )

    result = use_case.execute(code="token-ok", ip="10.0.0.1")

    assert result.status == "success"
    assert result.user == user
    assert len(repository.reactivate_calls) == 1
    assert repository.reactivate_calls[0]["token"] == token
    assert repository.reactivate_calls[0]["ip"] == "10.0.0.1"

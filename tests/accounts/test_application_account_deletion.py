import os
from datetime import timedelta
from types import SimpleNamespace

import django
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.accounts.application.account_deletion import (  # noqa: E402
    AccountDeletionUseCase,
)


class _FakeRepository:
    def __init__(self):
        self.calls = []

    def delete_account_and_issue_cancel_token(self, *, user, ip, expires_at):
        self.calls.append(
            {
                "user": user,
                "ip": ip,
                "expires_at": expires_at,
            }
        )
        return SimpleNamespace(id=77)


def test_account_deletion_use_case_issues_cancel_token_with_30_days_window():
    fake_repository = _FakeRepository()
    fixed_now = timezone.now()
    use_case = AccountDeletionUseCase(
        repository=fake_repository,
        now=lambda: fixed_now,
    )

    user = SimpleNamespace(id=10)
    result = use_case.execute(user=user, ip="127.0.0.1")

    assert result.token_id == 77
    assert len(fake_repository.calls) == 1
    recorded_call = fake_repository.calls[0]
    assert recorded_call["user"] == user
    assert recorded_call["ip"] == "127.0.0.1"
    assert recorded_call["expires_at"] == fixed_now + timedelta(days=30)

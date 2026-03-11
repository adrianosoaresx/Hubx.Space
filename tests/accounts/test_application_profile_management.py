import os
from types import SimpleNamespace

import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.accounts.application.profile_management import (  # noqa: E402
    ToggleUserStatusCommand,
    ToggleUserStatusUseCase,
)
from apps.backend.app.modules.accounts.domain.exceptions import (  # noqa: E402
    ProfileManagementPermissionDeniedError,
    UserAlreadyInactiveError,
)


def _actor(**kwargs):
    base = {
        "id": 100,
        "username": "admin",
        "get_tipo_usuario": "admin",
        "organizacao_id": 1,
        "is_authenticated": True,
    }
    base.update(kwargs)
    return SimpleNamespace(**base)


def _target(**kwargs):
    base = {
        "id": 200,
        "username": "alvo",
        "is_active": True,
        "organizacao_id": 1,
    }
    base.update(kwargs)
    return SimpleNamespace(**base)


class _FakeRepo:
    def __init__(self):
        self.saved = []
        self.events = []

    def save_active_status(self, *, user, is_active: bool) -> None:
        user.is_active = is_active
        self.saved.append((user.id, is_active))

    def create_security_event(self, *, user, event_name: str, ip: str | None) -> None:
        self.events.append((user.id, event_name, ip))


class _FakeAudit:
    def __init__(self):
        self.calls = []

    def log_status_change(self, *, actor, target, ip: str | None, is_active: bool) -> None:
        self.calls.append((actor.id, target.id, ip, is_active))


def _can_manage_same_org(actor, target):
    return actor.organizacao_id == target.organizacao_id


def test_deactivate_user_success():
    repo = _FakeRepo()
    audit = _FakeAudit()
    use_case = ToggleUserStatusUseCase(
        repository=repo,
        audit_logger=audit,
        can_manage_profile=_can_manage_same_org,
    )

    command = ToggleUserStatusCommand(actor=_actor(), target=_target(), ip="127.0.0.1")
    result = use_case.deactivate(command)

    assert result.is_active is False
    assert repo.saved == [(200, False)]
    assert repo.events == [(200, "usuario_desativado", "127.0.0.1")]
    assert audit.calls == [(100, 200, "127.0.0.1", False)]


def test_deactivate_user_without_permission_raises():
    repo = _FakeRepo()
    audit = _FakeAudit()
    use_case = ToggleUserStatusUseCase(
        repository=repo,
        audit_logger=audit,
        can_manage_profile=_can_manage_same_org,
    )

    command = ToggleUserStatusCommand(
        actor=_actor(organizacao_id=2),
        target=_target(organizacao_id=1),
        ip=None,
    )

    with pytest.raises(ProfileManagementPermissionDeniedError):
        use_case.deactivate(command)


def test_deactivate_already_inactive_user_raises():
    repo = _FakeRepo()
    audit = _FakeAudit()
    use_case = ToggleUserStatusUseCase(
        repository=repo,
        audit_logger=audit,
        can_manage_profile=_can_manage_same_org,
    )
    command = ToggleUserStatusCommand(actor=_actor(), target=_target(is_active=False), ip=None)

    with pytest.raises(UserAlreadyInactiveError):
        use_case.deactivate(command)

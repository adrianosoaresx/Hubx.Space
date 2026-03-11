from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from apps.backend.app.modules.accounts.domain.profile_management import (
    ensure_can_activate_user,
    ensure_can_deactivate_user,
    ensure_can_toggle_user_active,
    resolve_profile_section_template,
)


class UserStatusRepository(Protocol):
    def save_active_status(self, *, user, is_active: bool) -> None: ...

    def create_security_event(self, *, user, event_name: str, ip: str | None) -> None: ...


class UserStatusAuditLogger(Protocol):
    def log_status_change(self, *, actor, target, ip: str | None, is_active: bool) -> None: ...


@dataclass(frozen=True)
class ToggleUserStatusCommand:
    actor: object
    target: object
    ip: str | None


@dataclass(frozen=True)
class ToggleUserStatusResult:
    target_user_id: int
    is_active: bool
    event_name: str


class ToggleUserStatusUseCase:
    def __init__(
        self,
        *,
        repository: UserStatusRepository,
        audit_logger: UserStatusAuditLogger,
        can_manage_profile,
    ) -> None:
        self._repository = repository
        self._audit_logger = audit_logger
        self._can_manage_profile = can_manage_profile

    def deactivate(self, command: ToggleUserStatusCommand) -> ToggleUserStatusResult:
        ensure_can_toggle_user_active(
            command.actor,
            command.target,
            can_manage_profile=self._can_manage_profile,
        )
        ensure_can_deactivate_user(command.target)

        self._repository.save_active_status(user=command.target, is_active=False)
        self._repository.create_security_event(
            user=command.target,
            event_name="usuario_desativado",
            ip=command.ip,
        )
        self._audit_logger.log_status_change(
            actor=command.actor,
            target=command.target,
            ip=command.ip,
            is_active=False,
        )
        return ToggleUserStatusResult(
            target_user_id=command.target.id,
            is_active=False,
            event_name="usuario_desativado",
        )

    def activate(self, command: ToggleUserStatusCommand) -> ToggleUserStatusResult:
        ensure_can_toggle_user_active(
            command.actor,
            command.target,
            can_manage_profile=self._can_manage_profile,
        )
        ensure_can_activate_user(command.target)

        self._repository.save_active_status(user=command.target, is_active=True)
        self._repository.create_security_event(
            user=command.target,
            event_name="usuario_ativado",
            ip=command.ip,
        )
        self._audit_logger.log_status_change(
            actor=command.actor,
            target=command.target,
            ip=command.ip,
            is_active=True,
        )
        return ToggleUserStatusResult(
            target_user_id=command.target.id,
            is_active=True,
            event_name="usuario_ativado",
        )


class ResolveProfileSectionTemplateUseCase:
    def execute(self, *, section: str, can_manage: bool) -> str:
        return resolve_profile_section_template(section, can_manage=can_manage)

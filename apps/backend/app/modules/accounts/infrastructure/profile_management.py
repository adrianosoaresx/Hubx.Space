from __future__ import annotations

from accounts.models import SecurityEvent
from audit.services import hash_ip, log_audit


class DjangoUserStatusRepository:
    def save_active_status(self, *, user, is_active: bool) -> None:
        user.is_active = is_active
        user.save(update_fields=["is_active"])

    def create_security_event(self, *, user, event_name: str, ip: str | None) -> None:
        SecurityEvent.objects.create(
            usuario=user,
            evento=event_name,
            ip=ip,
        )


class DjangoUserStatusAuditLogger:
    def log_status_change(self, *, actor, target, ip: str | None, is_active: bool) -> None:
        action = "user_activated" if is_active else "user_deactivated"
        log_audit(
            actor,
            action,
            object_type="User",
            object_id=str(target.id),
            ip_hash=hash_ip(ip),
            metadata={"target_username": target.username},
        )

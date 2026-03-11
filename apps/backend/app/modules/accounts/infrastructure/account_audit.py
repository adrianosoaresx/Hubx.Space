from __future__ import annotations

from audit.models import AuditLog
from audit.services import hash_ip, log_audit


class DjangoAccountAuditLogger:
    def log_account_delete_canceled(self, *, user, ip: str | None) -> None:
        log_audit(
            user,
            "account_delete_canceled",
            object_type="User",
            object_id=str(user.id),
            ip_hash=hash_ip(ip or ""),
            status=AuditLog.Status.SUCCESS,
        )

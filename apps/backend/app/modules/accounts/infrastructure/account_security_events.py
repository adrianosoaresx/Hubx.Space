from __future__ import annotations

from accounts.models import SecurityEvent


class DjangoAccountSecurityEventLogger:
    def log_account_delete_failed(self, *, user, ip: str | None) -> None:
        SecurityEvent.objects.create(
            usuario=user,
            evento="conta_exclusao_falha",
            ip=ip,
        )

    def log_2fa_enable_failed(self, *, user, ip: str | None) -> None:
        SecurityEvent.objects.create(
            usuario=user,
            evento="2fa_habilitacao_falha",
            ip=ip,
        )

    def log_2fa_enabled(self, *, user, ip: str | None) -> None:
        SecurityEvent.objects.create(
            usuario=user,
            evento="2fa_habilitado",
            ip=ip,
        )

    def log_2fa_disable_failed(self, *, user, ip: str | None) -> None:
        SecurityEvent.objects.create(
            usuario=user,
            evento="2fa_desabilitacao_falha",
            ip=ip,
        )

    def log_2fa_disabled(self, *, user, ip: str | None) -> None:
        SecurityEvent.objects.create(
            usuario=user,
            evento="2fa_desabilitado",
            ip=ip,
        )

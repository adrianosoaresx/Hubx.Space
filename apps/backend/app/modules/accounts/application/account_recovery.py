from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Protocol

from apps.backend.app.modules.accounts.domain.account_recovery import is_token_invalid_or_expired


class AccountRecoveryRepository(Protocol):
    def find_user_by_email(self, *, email: str): ...

    def find_token_by_code(self, *, code: str, token_type: str): ...

    def invalidate_open_tokens(self, *, user, token_type: str, now) -> None: ...

    def create_token(self, *, user, token_type: str, expires_at, ip: str | None): ...

    def create_security_event(self, *, user, event_name: str, ip: str | None) -> None: ...

    def activate_user_email(self, *, user) -> None: ...

    def mark_token_used(self, *, token) -> None: ...

    def mark_token_confirmed(self, *, token) -> None: ...

    def save_user_password(self, *, user, raw_password: str) -> None: ...

    def validate_password(self, *, user, raw_password: str) -> list[str]: ...

    def clear_login_failures(self, *, user) -> None: ...

    def get_token_types(self) -> object: ...


class AccountRecoveryNotifier(Protocol):
    def send_confirmation_email(self, *, token_id: int) -> None: ...

    def send_password_reset_email(self, *, token_id: int) -> None: ...


@dataclass(frozen=True)
class GenericRequestResult:
    status: str


@dataclass(frozen=True)
class ConfirmEmailResult:
    status: str


@dataclass(frozen=True)
class ResetPasswordResult:
    status: str
    errors: list[str] | None = None


class AccountRecoveryUseCase:
    def __init__(
        self,
        *,
        repository: AccountRecoveryRepository,
        notifier: AccountRecoveryNotifier,
        now,
    ) -> None:
        self._repository = repository
        self._notifier = notifier
        self._now = now
        self._types = repository.get_token_types()

    def resend_confirmation(self, *, email: str | None, ip: str | None) -> GenericRequestResult:
        normalized_email = (email or "").strip()
        if not normalized_email:
            return GenericRequestResult(status="missing_email")

        user = self._repository.find_user_by_email(email=normalized_email)
        if user is None or getattr(user, "deleted", False):
            return GenericRequestResult(status="ignored")
        if user.is_active:
            return GenericRequestResult(status="already_active")

        now = self._now()
        self._repository.invalidate_open_tokens(
            user=user,
            token_type=self._types.EMAIL_CONFIRMATION,
            now=now,
        )
        token = self._repository.create_token(
            user=user,
            token_type=self._types.EMAIL_CONFIRMATION,
            expires_at=now + timedelta(hours=24),
            ip=ip,
        )
        self._notifier.send_confirmation_email(token_id=token.id)
        self._repository.create_security_event(
            user=user,
            event_name="resend_confirmation",
            ip=ip,
        )
        return GenericRequestResult(status="sent")

    def request_password_reset(self, *, email: str | None, ip: str | None) -> GenericRequestResult:
        normalized_email = (email or "").strip()
        if not normalized_email:
            return GenericRequestResult(status="missing_email")

        user = self._repository.find_user_by_email(email=normalized_email)
        if user is None:
            return GenericRequestResult(status="ignored")

        now = self._now()
        self._repository.invalidate_open_tokens(
            user=user,
            token_type=self._types.PASSWORD_RESET,
            now=now,
        )
        token = self._repository.create_token(
            user=user,
            token_type=self._types.PASSWORD_RESET,
            expires_at=now + timedelta(hours=1),
            ip=ip,
        )
        self._notifier.send_password_reset_email(token_id=token.id)
        self._repository.create_security_event(
            user=user,
            event_name="senha_reset_solicitada",
            ip=ip,
        )
        return GenericRequestResult(status="sent")

    def confirm_email_token(self, *, code: str | None, ip: str | None) -> ConfirmEmailResult:
        if not code:
            return ConfirmEmailResult(status="missing_token")

        token = self._repository.find_token_by_code(
            code=code,
            token_type=self._types.EMAIL_CONFIRMATION,
        )
        if token is None:
            return ConfirmEmailResult(status="invalid")

        self._repository.create_security_event(
            user=token.usuario,
            event_name="email_confirmacao_link_acessado",
            ip=ip,
        )
        now = self._now()
        if token.used_at:
            self._repository.create_security_event(
                user=token.usuario,
                event_name="email_confirmacao_falha",
                ip=ip,
            )
            return ConfirmEmailResult(status="already_used")
        if is_token_invalid_or_expired(token=token, now=now):
            self._repository.create_security_event(
                user=token.usuario,
                event_name="email_confirmacao_falha",
                ip=ip,
            )
            return ConfirmEmailResult(status="expired")

        self._repository.activate_user_email(user=token.usuario)
        self._repository.mark_token_used(token=token)
        self._repository.create_security_event(
            user=token.usuario,
            event_name="email_confirmado",
            ip=ip,
        )
        return ConfirmEmailResult(status="success")

    def find_password_reset_token(self, *, code: str):
        return self._repository.find_token_by_code(
            code=code,
            token_type=self._types.PASSWORD_RESET,
        )

    def evaluate_password_reset_token(self, *, token, ip: str | None) -> GenericRequestResult:
        if token is None:
            return GenericRequestResult(status="invalid")
        if is_token_invalid_or_expired(token=token, now=self._now()):
            self._repository.create_security_event(
                user=token.usuario,
                event_name="senha_redefinicao_falha",
                ip=ip,
            )
            return GenericRequestResult(status="invalid")
        return GenericRequestResult(status="valid")

    def mark_password_reset_token_confirmed(self, *, token) -> None:
        if token.status == token.Status.PENDENTE:
            self._repository.mark_token_confirmed(token=token)

    def reset_password(self, *, code: str | None, raw_password: str | None, ip: str | None) -> ResetPasswordResult:
        if not code or not raw_password:
            return ResetPasswordResult(status="missing_data")
        token = self.find_password_reset_token(code=code)
        state = self.evaluate_password_reset_token(token=token, ip=ip)
        if state.status != "valid":
            return ResetPasswordResult(status="invalid_token")

        errors = self._repository.validate_password(user=token.usuario, raw_password=raw_password)
        if errors:
            return ResetPasswordResult(status="invalid_password", errors=errors)

        self._repository.clear_login_failures(user=token.usuario)
        self._repository.save_user_password(user=token.usuario, raw_password=raw_password)
        self._repository.create_security_event(
            user=token.usuario,
            event_name="senha_redefinida",
            ip=ip,
        )
        self._repository.mark_token_used(token=token)
        return ResetPasswordResult(status="success")

    def finalize_web_password_reset(self, *, token, ip: str | None) -> None:
        self._repository.clear_login_failures(user=token.usuario)
        self._repository.mark_token_used(token=token)
        self._repository.create_security_event(
            user=token.usuario,
            event_name="senha_redefinida",
            ip=ip,
        )

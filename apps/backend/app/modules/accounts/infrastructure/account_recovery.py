from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils import timezone

from accounts.auth import clear_login_failures
from accounts.models import AccountToken, SecurityEvent
from accounts.tasks import send_confirmation_email, send_password_reset_email

User = get_user_model()


class DjangoAccountRecoveryRepository:
    def find_user_by_email(self, *, email: str):
        try:
            return User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return None

    def find_token_by_code(self, *, code: str, token_type: str):
        try:
            return AccountToken.objects.select_related("usuario").get(
                codigo=code,
                tipo=token_type,
            )
        except AccountToken.DoesNotExist:
            return None

    def invalidate_open_tokens(self, *, user, token_type: str, now) -> None:
        AccountToken.objects.filter(
            usuario=user,
            tipo=token_type,
            used_at__isnull=True,
        ).update(used_at=now, status=AccountToken.Status.UTILIZADO)

    def create_token(self, *, user, token_type: str, expires_at, ip: str | None):
        return AccountToken.objects.create(
            usuario=user,
            tipo=token_type,
            expires_at=expires_at,
            ip_gerado=ip,
        )

    def create_security_event(self, *, user, event_name: str, ip: str | None) -> None:
        SecurityEvent.objects.create(
            usuario=user,
            evento=event_name,
            ip=ip,
        )

    def activate_user_email(self, *, user) -> None:
        user.is_active = True
        user.email_confirmed = True
        user.save(update_fields=["is_active", "email_confirmed"])

    def mark_token_used(self, *, token) -> None:
        token.mark_used()

    def mark_token_confirmed(self, *, token) -> None:
        token.mark_confirmed()

    def save_user_password(self, *, user, raw_password: str) -> None:
        user.set_password(raw_password)
        user.save(update_fields=["password"])

    def validate_password(self, *, user, raw_password: str) -> list[str]:
        try:
            validate_password(raw_password, user)
        except ValidationError as exc:
            return list(exc.messages)
        return []

    def clear_login_failures(self, *, user) -> None:
        clear_login_failures(user)
        cache.delete(f"failed_login_attempts_user_{user.pk}")
        cache.delete(f"lockout_user_{user.pk}")

    def get_token_types(self) -> object:
        return AccountToken.Tipo


class CeleryAccountRecoveryNotifier:
    def send_confirmation_email(self, *, token_id: int) -> None:
        send_confirmation_email.delay(token_id)

    def send_password_reset_email(self, *, token_id: int) -> None:
        send_password_reset_email.delay(token_id)


def now_provider():
    return timezone.now()

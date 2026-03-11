from __future__ import annotations

from django.db import transaction

from accounts.models import AccountToken, SecurityEvent


class DjangoAccountDeleteCancellationRepository:
    def find_cancel_delete_token(self, *, code: str):
        try:
            return AccountToken.objects.select_related("usuario").get(
                codigo=code,
                tipo=AccountToken.Tipo.CANCEL_DELETE,
            )
        except AccountToken.DoesNotExist:
            return None

    def reactivate_user_from_cancel_token(self, *, token, ip: str | None):
        with transaction.atomic():
            user = token.usuario
            user.deleted = False
            user.deleted_at = None
            user.is_active = True
            user.exclusao_confirmada = False
            user.save(update_fields=["deleted", "deleted_at", "is_active", "exclusao_confirmada"])
            token.mark_used()
            SecurityEvent.objects.create(
                usuario=user,
                evento="cancelou_exclusao",
                ip=ip,
            )
        return user

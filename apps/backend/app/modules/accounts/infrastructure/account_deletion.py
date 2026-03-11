from __future__ import annotations

from django.db import transaction

from accounts.models import AccountToken, SecurityEvent


class DjangoAccountDeletionRepository:
    def delete_account_and_issue_cancel_token(
        self,
        *,
        user,
        ip: str | None,
        expires_at,
    ):
        with transaction.atomic():
            user.exclusao_confirmada = True
            user.is_active = False
            user.save(update_fields=["exclusao_confirmada", "is_active"])
            user.delete()
            SecurityEvent.objects.create(
                usuario=user,
                evento="conta_excluida",
                ip=ip,
            )
            token = AccountToken.objects.create(
                usuario=user,
                tipo=AccountToken.Tipo.CANCEL_DELETE,
                expires_at=expires_at,
                ip_gerado=ip,
            )
        return token

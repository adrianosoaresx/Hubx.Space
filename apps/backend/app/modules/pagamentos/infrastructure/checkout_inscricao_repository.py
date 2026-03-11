from __future__ import annotations

from uuid import UUID

from eventos.models import InscricaoEvento
from pagamentos.models import Transacao


class DjangoCheckoutInscricaoRepository:
    def find_accessible_inscricao(
        self,
        *,
        inscricao_uuid: str | UUID | None,
        user,
        include_deleted: bool = False,
    ) -> InscricaoEvento | None:
        if not inscricao_uuid or not getattr(user, "is_authenticated", False):
            return None
        manager = InscricaoEvento.all_objects if include_deleted else InscricaoEvento.objects
        try:
            inscricao = manager.select_related("user", "evento").get(uuid=inscricao_uuid)
        except InscricaoEvento.DoesNotExist:
            return None
        if inscricao.user != user:
            return None
        return inscricao

    def register_faturamento(
        self,
        *,
        inscricao: InscricaoEvento,
        condicao_faturamento: str,
    ) -> InscricaoEvento:
        inscricao.metodo_pagamento = "faturamento"
        inscricao.condicao_faturamento = condicao_faturamento
        inscricao.valor_pago = None
        inscricao.pagamento_validado = False
        inscricao.transacao = None
        update_fields = [
            "metodo_pagamento",
            "condicao_faturamento",
            "valor_pago",
            "transacao",
            "pagamento_validado",
            "updated_at",
        ]
        if inscricao.deleted:
            inscricao.deleted = False
            inscricao.deleted_at = None
            update_fields.extend(["deleted", "deleted_at"])
        inscricao.save(update_fields=update_fields)
        return inscricao

    def link_transacao(
        self,
        *,
        inscricao: InscricaoEvento,
        transacao: Transacao,
    ) -> None:
        inscricao.transacao = transacao
        inscricao.metodo_pagamento = transacao.metodo
        inscricao.pagamento_validado = transacao.status == Transacao.Status.APROVADA
        inscricao.save(
            update_fields=["transacao", "metodo_pagamento", "pagamento_validado", "updated_at"]
        )

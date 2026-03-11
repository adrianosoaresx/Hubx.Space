from __future__ import annotations

from pagamentos.models import Transacao


class DjangoTransacaoReportingLookupRepository:
    def list_for_review(self, *, statuses: list[str]):
        return Transacao.objects.select_related("pedido").filter(status__in=statuses).order_by("-criado_em")

    def list_for_csv(self):
        return Transacao.objects.select_related("pedido").order_by("-criado_em")

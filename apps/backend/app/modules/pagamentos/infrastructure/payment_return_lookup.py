from __future__ import annotations

from pagamentos.models import Transacao


class DjangoPaymentReturnLookupRepository:
    def find_transaction(self, *, payment_token: str | None, payment_id: str | None):
        queryset = Transacao.objects.select_related("pedido", "pedido__organizacao")
        if payment_token:
            transacao = queryset.filter(external_id=str(payment_token)).first()
            if transacao:
                return transacao
            transacao = queryset.filter(detalhes__payment_token=str(payment_token)).first()
            if transacao:
                return transacao
        if payment_id:
            return queryset.filter(external_id=str(payment_id)).first()
        return None

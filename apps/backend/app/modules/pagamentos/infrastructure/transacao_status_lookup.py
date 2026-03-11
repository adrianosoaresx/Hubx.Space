from __future__ import annotations

from eventos.models import InscricaoEvento
from pagamentos.models import Transacao


class DjangoTransacaoStatusLookupRepository:
    def get_transacao(self, *, pk: int) -> Transacao | None:
        return Transacao.objects.select_related("pedido").filter(pk=pk).first()

    def get_inscricao_evento(self, *, transacao: Transacao) -> InscricaoEvento | None:
        try:
            return transacao.inscricao_evento
        except InscricaoEvento.DoesNotExist:
            return None

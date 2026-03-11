from __future__ import annotations

from dataclasses import dataclass

from pagamentos.models import Transacao


@dataclass(frozen=True)
class TransacaoStatusDecision:
    should_sync_payment_model: bool
    should_redirect_hx_to_inscricao: bool
    should_render_inscricao_result: bool


class TransacaoStatusUseCase:
    def decide(self, *, status: str, has_inscricao: bool, is_htmx_request: bool) -> TransacaoStatusDecision:
        should_sync = status == Transacao.Status.PENDENTE
        should_redirect_hx = status == Transacao.Status.APROVADA and has_inscricao and is_htmx_request
        should_render_inscricao = status == Transacao.Status.APROVADA and has_inscricao and not is_htmx_request
        return TransacaoStatusDecision(
            should_sync_payment_model=should_sync,
            should_redirect_hx_to_inscricao=should_redirect_hx,
            should_render_inscricao_result=should_render_inscricao,
        )

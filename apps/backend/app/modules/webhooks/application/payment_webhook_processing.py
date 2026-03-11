from __future__ import annotations

from typing import Any, Callable

from eventos.models import InscricaoEvento
from pagamentos.models import Transacao
from pagamentos.services import PagamentoService


def find_transaction_by_external_id(external_id: str) -> Transacao | None:
    return (
        Transacao.objects.select_related("pedido", "pedido__organizacao")
        .filter(external_id=external_id)
        .first()
    )


def build_provider_for_webhook(
    provider_class: type[Any], organizacao: Any | None
) -> Any:
    if hasattr(provider_class, "from_organizacao"):
        return provider_class.from_organizacao(organizacao)
    return provider_class()


def confirm_known_transaction(
    *,
    provider_class: type[Any],
    organizacao: Any | None,
    transacao: Transacao,
    confirmar_pagamento_com_retry: Callable[[PagamentoService, Transacao], None],
) -> None:
    provider = build_provider_for_webhook(provider_class, organizacao)
    service = PagamentoService(provider)
    confirmar_pagamento_com_retry(service, transacao)


def atualizar_inscricao_transacao_aprovada(
    *,
    transacao: Transacao,
    logger: Any,
) -> None:
    try:
        inscricao = transacao.inscricao_evento
    except InscricaoEvento.DoesNotExist:
        return

    if transacao.status != Transacao.Status.APROVADA:
        return

    try:
        inscricao.pagamento_validado = True
        inscricao.transacao = transacao
        inscricao.confirmar_inscricao()
    except Exception:
        logger.exception(
            "webhook_inscricao_confirmacao_falhou",
            extra={"inscricao_id": inscricao.pk, "transacao_id": transacao.pk},
        )

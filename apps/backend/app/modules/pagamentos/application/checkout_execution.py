from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

from pagamentos.exceptions import PagamentoProviderError
from pagamentos.models import Transacao
from pagamentos.providers import MercadoPagoProvider
from pagamentos.services import PagamentoService

from apps.backend.app.modules.pagamentos.application.checkout_workflow import (
    PixCheckoutCommandResult,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PixCheckoutExecutionResult:
    success: bool
    transacao: Transacao | None
    error_message: str | None
    provider_public_key: str | None


def execute_pix_checkout_payment(
    *,
    command_result: PixCheckoutCommandResult,
    vincular_transacao: Callable[[Transacao], None],
) -> PixCheckoutExecutionResult:
    provider = MercadoPagoProvider.from_organizacao(command_result.organizacao)
    service = PagamentoService(provider)
    try:
        transacao = service.iniciar_pagamento(
            command_result.pedido,
            command_result.metodo_pagamento,
            command_result.dados_pagamento,
        )
        vincular_transacao(transacao)
    except PagamentoProviderError as exc:
        return PixCheckoutExecutionResult(
            success=False,
            transacao=None,
            error_message=str(exc),
            provider_public_key=provider.public_key,
        )
    except Exception:
        logger.exception(
            "erro_checkout_pagamento",
            extra={
                "pedido_id": command_result.pedido.id,
                "metodo": command_result.metodo_pagamento,
            },
        )
        raise

    return PixCheckoutExecutionResult(
        success=True,
        transacao=transacao,
        error_message=None,
        provider_public_key=provider.public_key,
    )

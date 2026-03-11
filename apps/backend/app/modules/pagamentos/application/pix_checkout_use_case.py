from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from pagamentos.models import Transacao

from apps.backend.app.modules.pagamentos.application.checkout_execution import (
    PixCheckoutExecutionResult,
    execute_pix_checkout_payment,
)
from apps.backend.app.modules.pagamentos.application.checkout_workflow import (
    build_pix_checkout_command_input,
    prepare_pix_checkout_command,
)


@dataclass(frozen=True)
class PixCheckoutUseCaseResult:
    success: bool
    transacao: Transacao | None
    error_message: str | None
    provider_public_key: str | None


def execute_pix_checkout_use_case(
    *,
    cleaned_data: dict[str, object],
    default_organizacao,
    resolve_organizacao: Callable[[str | None], object | None],
    vincular_transacao: Callable[[Transacao], None],
) -> PixCheckoutUseCaseResult:
    command_input = build_pix_checkout_command_input(cleaned_data=cleaned_data)
    command_result = prepare_pix_checkout_command(
        default_organizacao=default_organizacao,
        command_input=command_input,
        resolve_organizacao=resolve_organizacao,
    )
    execution_result: PixCheckoutExecutionResult = execute_pix_checkout_payment(
        command_result=command_result,
        vincular_transacao=vincular_transacao,
    )

    return PixCheckoutUseCaseResult(
        success=execution_result.success,
        transacao=execution_result.transacao,
        error_message=execution_result.error_message,
        provider_public_key=execution_result.provider_public_key,
    )

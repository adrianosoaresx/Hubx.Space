from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode
from typing import Callable

from django.urls import reverse
from django.utils.translation import gettext as _


@dataclass(frozen=True)
class FaturamentoCheckoutInput:
    inscricao_uuid: str | None
    condicao_faturamento: str | None


@dataclass(frozen=True)
class FaturamentoCheckoutResult:
    success: bool
    error_message: str | None
    redirect_url: str | None


def build_faturamento_checkout_input(
    *, cleaned_data: dict[str, object]
) -> FaturamentoCheckoutInput:
    inscricao_raw = cleaned_data.get("inscricao_uuid")
    condicao_raw = cleaned_data.get("condicao_faturamento")
    return FaturamentoCheckoutInput(
        inscricao_uuid=str(inscricao_raw).strip() if inscricao_raw else None,
        condicao_faturamento=str(condicao_raw).strip() if condicao_raw else None,
    )


def execute_faturamento_checkout_use_case(
    *,
    checkout_input: FaturamentoCheckoutInput,
    registrar_faturamento: Callable[[str | None, str | None], object | None],
) -> FaturamentoCheckoutResult:
    inscricao = registrar_faturamento(
        checkout_input.inscricao_uuid,
        checkout_input.condicao_faturamento,
    )
    if not inscricao:
        return FaturamentoCheckoutResult(
            success=False,
            error_message=_("Não foi possível localizar a inscrição para faturamento."),
            redirect_url=None,
        )

    resultado_url = reverse("eventos:inscricao_resultado", kwargs={"uuid": inscricao.uuid})
    mensagem = _("Faturamento registrado, aguardando validação da equipe financeira.")
    querystring = urlencode({"status": "info", "message": mensagem})
    return FaturamentoCheckoutResult(
        success=True,
        error_message=None,
        redirect_url=f"{resultado_url}?{querystring}",
    )

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Callable

from django.utils.translation import gettext as _

from pagamentos.models import Pedido, Transacao


@dataclass(frozen=True)
class PixCheckoutCommandInput:
    valor: Decimal
    email: str | None
    nome: str | None
    documento: str | None
    metodo: str | None
    token_cartao: str | None
    payment_method_id: str | None
    parcelas: int | None
    vencimento: datetime | None
    pix_expiracao: datetime | None
    organizacao_id: str | None


@dataclass(frozen=True)
class PixCheckoutCommandResult:
    pedido: Pedido
    organizacao: object | None
    metodo_pagamento: str
    dados_pagamento: dict[str, object]


def build_pix_checkout_command_input(
    *, cleaned_data: dict[str, object]
) -> PixCheckoutCommandInput:
    return PixCheckoutCommandInput(
        valor=cleaned_data["valor"],
        email=cleaned_data.get("email"),
        nome=cleaned_data.get("nome"),
        documento=cleaned_data.get("documento"),
        metodo=cleaned_data.get("metodo"),
        token_cartao=cleaned_data.get("token_cartao"),
        payment_method_id=cleaned_data.get("payment_method_id"),
        parcelas=cleaned_data.get("parcelas"),
        vencimento=cleaned_data.get("vencimento"),
        pix_expiracao=cleaned_data.get("pix_expiracao"),
        organizacao_id=str(cleaned_data.get("organizacao_id") or "").strip() or None,
    )


def prepare_pix_checkout_command(
    *,
    default_organizacao,
    command_input: PixCheckoutCommandInput,
    resolve_organizacao: Callable[[str | None], object | None],
) -> PixCheckoutCommandResult:
    organizacao = (
        resolve_organizacao(command_input.organizacao_id) or default_organizacao
    )

    pedido = Pedido.objects.create(
        valor=command_input.valor,
        email=command_input.email,
        nome=command_input.nome,
        organizacao=organizacao,
    )

    metodo_pagamento = command_input.metodo or Transacao.Metodo.PIX
    dados_pagamento: dict[str, object] = {
        "email": command_input.email,
        "nome": command_input.nome,
        "document_number": command_input.documento,
        "document_type": "CPF",
    }
    if metodo_pagamento == Transacao.Metodo.CARTAO:
        dados_pagamento.update(
            {
                "token": command_input.token_cartao,
                "payment_method_id": command_input.payment_method_id,
                "parcelas": command_input.parcelas or 1,
            }
        )
    elif metodo_pagamento == Transacao.Metodo.BOLETO:
        dados_pagamento.update({"vencimento": command_input.vencimento})
    elif metodo_pagamento == Transacao.Metodo.PIX:
        dados_pagamento.update(
            {
                "descricao": _("Pagamento Hubx"),
                "expiracao": command_input.pix_expiracao,
            }
        )

    return PixCheckoutCommandResult(
        pedido=pedido,
        organizacao=organizacao,
        metodo_pagamento=metodo_pagamento,
        dados_pagamento=dados_pagamento,
    )

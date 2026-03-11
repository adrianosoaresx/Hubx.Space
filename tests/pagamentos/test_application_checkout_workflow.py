from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
import os

import django
import pytest
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.pagamentos.application.checkout_workflow import (
    build_pix_checkout_command_input,
    prepare_pix_checkout_command,
)
from organizacoes.models import Organizacao
from pagamentos.models import Transacao


def _create_org(name: str, suffix: int) -> Organizacao:
    return Organizacao.objects.create(
        nome=name,
        cnpj=f"55443322{suffix:04d}95",
    )


@pytest.mark.django_db
def test_build_pix_checkout_command_input_normaliza_campos():
    expires_at = timezone.now() + timedelta(minutes=30)
    cleaned_data = {
        "valor": Decimal("150.00"),
        "email": "cliente@example.com",
        "nome": "Cliente",
        "documento": "12345678909",
        "metodo": Transacao.Metodo.PIX,
        "token_cartao": None,
        "payment_method_id": None,
        "parcelas": None,
        "vencimento": None,
        "pix_expiracao": expires_at,
        "organizacao_id": "  ",
    }

    command_input = build_pix_checkout_command_input(cleaned_data=cleaned_data)

    assert command_input.valor == Decimal("150.00")
    assert command_input.metodo == Transacao.Metodo.PIX
    assert command_input.pix_expiracao == expires_at
    assert command_input.organizacao_id is None


@pytest.mark.django_db
def test_prepare_pix_checkout_command_resolve_organizacao_e_payload_pix():
    org_default = _create_org("Org Default", 1001)
    org_selected = _create_org("Org Selected", 1002)
    expires_at = timezone.now() + timedelta(minutes=45)
    command_input = build_pix_checkout_command_input(
        cleaned_data={
            "valor": Decimal("200.00"),
            "email": "checkout@example.com",
            "nome": "Checkout",
            "documento": "98765432100",
            "metodo": Transacao.Metodo.PIX,
            "token_cartao": None,
            "payment_method_id": None,
            "parcelas": None,
            "vencimento": None,
            "pix_expiracao": expires_at,
            "organizacao_id": str(org_selected.id),
        }
    )

    resolved_ids: list[str | None] = []

    def _resolve(organizacao_id: str | None):
        resolved_ids.append(organizacao_id)
        return org_selected

    result = prepare_pix_checkout_command(
        default_organizacao=org_default,
        command_input=command_input,
        resolve_organizacao=_resolve,
    )

    assert resolved_ids == [str(org_selected.id)]
    assert result.organizacao == org_selected
    assert result.pedido.organizacao == org_selected
    assert result.metodo_pagamento == Transacao.Metodo.PIX
    assert result.dados_pagamento["descricao"] == "Pagamento Hubx"
    assert result.dados_pagamento["expiracao"] == expires_at


@pytest.mark.django_db
def test_prepare_pix_checkout_command_cartao_aplica_defaults():
    org_default = _create_org("Org Card", 1003)
    command_input = build_pix_checkout_command_input(
        cleaned_data={
            "valor": Decimal("300.00"),
            "email": "card@example.com",
            "nome": "Card Holder",
            "documento": "11122233344",
            "metodo": Transacao.Metodo.CARTAO,
            "token_cartao": "tok_abc",
            "payment_method_id": "visa",
            "parcelas": None,
            "vencimento": None,
            "pix_expiracao": None,
            "organizacao_id": None,
        }
    )

    result = prepare_pix_checkout_command(
        default_organizacao=org_default,
        command_input=command_input,
        resolve_organizacao=lambda _: None,
    )

    assert result.organizacao == org_default
    assert result.pedido.organizacao == org_default
    assert result.metodo_pagamento == Transacao.Metodo.CARTAO
    assert result.dados_pagamento["token"] == "tok_abc"
    assert result.dados_pagamento["payment_method_id"] == "visa"
    assert result.dados_pagamento["parcelas"] == 1

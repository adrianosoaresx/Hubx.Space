from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
import os

import django
import pytest
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.pagamentos.application.pix_checkout_use_case import (
    execute_pix_checkout_use_case,
)
from organizacoes.models import Organizacao
from pagamentos.exceptions import PagamentoProviderError
from pagamentos.models import Transacao
from pagamentos.services.pagamento import PagamentoService


def _create_org(suffix: int) -> Organizacao:
    return Organizacao.objects.create(
        nome=f"Org Pix UseCase {suffix}",
        cnpj=f"88997766{suffix:04d}95",
    )


def _cleaned_data(org: Organizacao) -> dict[str, object]:
    return {
        "valor": Decimal("99.90"),
        "email": "pix@example.com",
        "nome": "Pix User",
        "documento": "12345678909",
        "metodo": Transacao.Metodo.PIX,
        "token_cartao": None,
        "payment_method_id": None,
        "parcelas": None,
        "vencimento": None,
        "pix_expiracao": timezone.now() + timedelta(minutes=30),
        "organizacao_id": str(org.id),
    }


@pytest.mark.django_db
def test_execute_pix_checkout_use_case_sucesso(monkeypatch):
    org = _create_org(3001)

    def _fake_iniciar(self, pedido, metodo, _dados_pagamento):
        return Transacao.objects.create(
            pedido=pedido,
            valor=pedido.valor,
            status=Transacao.Status.APROVADA,
            metodo=metodo,
            detalhes={"status": "approved", "uc": True},
        )

    monkeypatch.setattr(PagamentoService, "iniciar_pagamento", _fake_iniciar)

    linked = {}
    result = execute_pix_checkout_use_case(
        cleaned_data=_cleaned_data(org),
        default_organizacao=org,
        resolve_organizacao=lambda _org_id: org,
        vincular_transacao=lambda transacao: linked.update({"id": transacao.id}),
    )

    assert result.success is True
    assert result.transacao is not None
    assert result.error_message is None
    assert linked["id"] == result.transacao.id


@pytest.mark.django_db
def test_execute_pix_checkout_use_case_provider_error(monkeypatch):
    org = _create_org(3002)

    def _fake_iniciar(_self, _pedido, _metodo, _dados_pagamento):
        raise PagamentoProviderError("erro de provider")

    monkeypatch.setattr(PagamentoService, "iniciar_pagamento", _fake_iniciar)

    result = execute_pix_checkout_use_case(
        cleaned_data=_cleaned_data(org),
        default_organizacao=org,
        resolve_organizacao=lambda _org_id: org,
        vincular_transacao=lambda _transacao: None,
    )

    assert result.success is False
    assert result.transacao is None
    assert result.error_message == "erro de provider"

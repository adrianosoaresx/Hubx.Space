from __future__ import annotations

from decimal import Decimal
import os

import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.pagamentos.application.checkout_execution import (
    execute_pix_checkout_payment,
)
from apps.backend.app.modules.pagamentos.application.checkout_workflow import (
    PixCheckoutCommandResult,
)
from organizacoes.models import Organizacao
from pagamentos.exceptions import PagamentoProviderError
from pagamentos.models import Pedido, Transacao


def _create_org(suffix: int) -> Organizacao:
    return Organizacao.objects.create(
        nome=f"Org Execution {suffix}",
        cnpj=f"77665544{suffix:04d}95",
    )


def _build_command_result(org: Organizacao) -> PixCheckoutCommandResult:
    pedido = Pedido.objects.create(
        valor=Decimal("180.00"),
        email="checkout@example.com",
        nome="Checkout",
        organizacao=org,
    )
    return PixCheckoutCommandResult(
        pedido=pedido,
        organizacao=org,
        metodo_pagamento=Transacao.Metodo.PIX,
        dados_pagamento={
            "email": "checkout@example.com",
            "nome": "Checkout",
            "document_number": "12345678909",
            "document_type": "CPF",
            "descricao": "Pagamento Hubx",
        },
    )


class _FakeProvider:
    public_key = "fake-public-key"


@pytest.mark.django_db
def test_execute_pix_checkout_payment_sucesso(monkeypatch):
    org = _create_org(2001)
    command_result = _build_command_result(org)

    monkeypatch.setattr(
        "apps.backend.app.modules.pagamentos.application.checkout_execution.MercadoPagoProvider.from_organizacao",
        lambda _: _FakeProvider(),
    )

    def _fake_iniciar(self, pedido, metodo, dados_pagamento):
        return Transacao.objects.create(
            pedido=pedido,
            valor=pedido.valor,
            status=Transacao.Status.APROVADA,
            metodo=metodo,
            detalhes={"status": "approved"},
        )

    monkeypatch.setattr(
        "apps.backend.app.modules.pagamentos.application.checkout_execution.PagamentoService.iniciar_pagamento",
        _fake_iniciar,
    )

    linked = {}
    result = execute_pix_checkout_payment(
        command_result=command_result,
        vincular_transacao=lambda transacao: linked.update({"id": transacao.id}),
    )

    assert result.success is True
    assert result.transacao is not None
    assert result.error_message is None
    assert result.provider_public_key == "fake-public-key"
    assert linked["id"] == result.transacao.id


@pytest.mark.django_db
def test_execute_pix_checkout_payment_provider_error(monkeypatch):
    org = _create_org(2002)
    command_result = _build_command_result(org)

    monkeypatch.setattr(
        "apps.backend.app.modules.pagamentos.application.checkout_execution.MercadoPagoProvider.from_organizacao",
        lambda _: _FakeProvider(),
    )

    def _fake_iniciar(_self, _pedido, _metodo, _dados_pagamento):
        raise PagamentoProviderError("falha controlada")

    monkeypatch.setattr(
        "apps.backend.app.modules.pagamentos.application.checkout_execution.PagamentoService.iniciar_pagamento",
        _fake_iniciar,
    )

    result = execute_pix_checkout_payment(
        command_result=command_result,
        vincular_transacao=lambda _transacao: None,
    )

    assert result.success is False
    assert result.transacao is None
    assert result.error_message == "falha controlada"
    assert result.provider_public_key == "fake-public-key"


@pytest.mark.django_db
def test_execute_pix_checkout_payment_erro_inesperado_repassa_excecao(monkeypatch):
    org = _create_org(2003)
    command_result = _build_command_result(org)

    monkeypatch.setattr(
        "apps.backend.app.modules.pagamentos.application.checkout_execution.MercadoPagoProvider.from_organizacao",
        lambda _: _FakeProvider(),
    )

    def _fake_iniciar(_self, _pedido, _metodo, _dados_pagamento):
        raise RuntimeError("falha inesperada")

    monkeypatch.setattr(
        "apps.backend.app.modules.pagamentos.application.checkout_execution.PagamentoService.iniciar_pagamento",
        _fake_iniciar,
    )

    with pytest.raises(RuntimeError, match="falha inesperada"):
        execute_pix_checkout_payment(
            command_result=command_result,
            vincular_transacao=lambda _transacao: None,
        )

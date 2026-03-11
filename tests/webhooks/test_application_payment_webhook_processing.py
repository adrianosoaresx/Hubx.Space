from __future__ import annotations

import os
from decimal import Decimal
from types import SimpleNamespace
from typing import Any

import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from eventos.models import InscricaoEvento
from organizacoes.models import Organizacao
from pagamentos.models import Pedido, Transacao

from apps.backend.app.modules.webhooks.application.payment_webhook_processing import (
    atualizar_inscricao_transacao_aprovada,
    build_provider_for_webhook,
    confirm_known_transaction,
    find_transaction_by_external_id,
)
from pagamentos.providers.base import PaymentProvider


def _create_transacao(external_id: str = "tx-known-1") -> Transacao:
    org = Organizacao.objects.create(
        nome=f"Org {external_id}",
        cnpj=f"12345678{Pedido.objects.count() + 1000:04d}95",
    )
    pedido = Pedido.objects.create(
        organizacao=org,
        valor=Decimal("100.00"),
        status=Pedido.Status.PENDENTE,
    )
    return Transacao.objects.create(
        pedido=pedido,
        metodo=Transacao.Metodo.PIX,
        valor=Decimal("100.00"),
        status=Transacao.Status.PENDENTE,
        external_id=external_id,
    )


class _ProviderWithFactory:
    @classmethod
    def from_organizacao(cls, organizacao: Any) -> dict[str, Any]:
        return {"provider": "factory", "organizacao_id": getattr(organizacao, "id", None)}


class _ProviderSimple:
    def __init__(self) -> None:
        self.name = "simple"


class _DummyPaymentProvider(PaymentProvider):
    def criar_cobranca(self, pedido, metodo, dados_pagamento=None):  # pragma: no cover
        return {"status": "pending"}

    def confirmar_pagamento(self, transacao):  # pragma: no cover
        return {"status": "approved"}

    def estornar_pagamento(self, transacao):  # pragma: no cover
        return {"status": "refunded"}

    def consultar_pagamento(self, transacao):  # pragma: no cover
        return {"status": "approved"}


class _ProviderForConfirm:
    @classmethod
    def from_organizacao(cls, organizacao):
        return _DummyPaymentProvider()


@pytest.mark.django_db
def test_find_transaction_by_external_id_retorna_transacao_quando_existe():
    transacao = _create_transacao("tx-known-1111")

    resultado = find_transaction_by_external_id("tx-known-1111")

    assert resultado is not None
    assert resultado.pk == transacao.pk


@pytest.mark.django_db
def test_find_transaction_by_external_id_retorna_none_quando_nao_existe():
    assert find_transaction_by_external_id("nao-existe") is None


def test_build_provider_for_webhook_usa_from_organizacao_quando_disponivel():
    org = SimpleNamespace(id=123)

    provider = build_provider_for_webhook(_ProviderWithFactory, org)

    assert provider == {"provider": "factory", "organizacao_id": 123}


def test_build_provider_for_webhook_instancia_classe_quando_sem_factory():
    provider = build_provider_for_webhook(_ProviderSimple, None)
    assert isinstance(provider, _ProviderSimple)


@pytest.mark.django_db
def test_confirm_known_transaction_delega_para_callback_de_retry():
    transacao = _create_transacao("tx-known-2222")
    called = {}

    def _fake_retry(service, tx):
        called["service"] = service
        called["transacao"] = tx

    confirm_known_transaction(
        provider_class=_ProviderForConfirm,
        organizacao=transacao.pedido.organizacao,
        transacao=transacao,
        confirmar_pagamento_com_retry=_fake_retry,
    )

    assert called["transacao"] == transacao
    assert called["service"].provider.__class__ is _DummyPaymentProvider


def test_atualizar_inscricao_transacao_aprovada_ignora_quando_sem_inscricao():
    class _TransacaoSemInscricao:
        pk = 1
        status = Transacao.Status.APROVADA

        @property
        def inscricao_evento(self):
            raise InscricaoEvento.DoesNotExist

    logger = SimpleNamespace(exception=lambda *args, **kwargs: None)
    atualizar_inscricao_transacao_aprovada(transacao=_TransacaoSemInscricao(), logger=logger)


def test_atualizar_inscricao_transacao_aprovada_ignora_quando_status_nao_aprovado():
    chamada = {"confirmou": False}

    class _InscricaoFake:
        pk = 10
        pagamento_validado = False
        transacao = None

        def confirmar_inscricao(self):
            chamada["confirmou"] = True

    transacao = SimpleNamespace(pk=20, status=Transacao.Status.PENDENTE, inscricao_evento=_InscricaoFake())
    logger = SimpleNamespace(exception=lambda *args, **kwargs: None)

    atualizar_inscricao_transacao_aprovada(transacao=transacao, logger=logger)

    assert chamada["confirmou"] is False


def test_atualizar_inscricao_transacao_aprovada_confirma_inscricao():
    chamada = {"confirmou": False}

    class _InscricaoFake:
        pk = 10
        pagamento_validado = False
        transacao = None

        def confirmar_inscricao(self):
            chamada["confirmou"] = True

    transacao = SimpleNamespace(pk=20, status=Transacao.Status.APROVADA, inscricao_evento=_InscricaoFake())
    logger = SimpleNamespace(exception=lambda *args, **kwargs: None)

    atualizar_inscricao_transacao_aprovada(transacao=transacao, logger=logger)

    assert chamada["confirmou"] is True
    assert transacao.inscricao_evento.pagamento_validado is True
    assert transacao.inscricao_evento.transacao == transacao

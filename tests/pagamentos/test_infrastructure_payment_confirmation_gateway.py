import os
from types import SimpleNamespace

import django
import pytest
from django.db import OperationalError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.pagamentos.infrastructure.payment_confirmation_gateway import (  # noqa: E402
    DjangoPaymentConfirmationGateway,
)


class _FakeLogger:
    def __init__(self):
        self.warnings = []

    def warning(self, message, extra=None):
        self.warnings.append({"message": message, "extra": extra or {}})


class _FakeService:
    def __init__(self, fail_times=0):
        self.fail_times = fail_times
        self.calls = 0

    def confirmar_pagamento(self, _transacao):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise OperationalError("db locked")


class _FakeTransacao:
    def __init__(self):
        self.id = 10
        self.status = "pending"
        self.external_id = None
        self.detalhes = {"payment_id": "pay_1"}
        self.saved_update_fields = None

    def save(self, *, update_fields):
        self.saved_update_fields = update_fields


def test_confirm_with_retry_eventually_succeeds():
    logger = _FakeLogger()
    gateway = DjangoPaymentConfirmationGateway(
        payment_model_getter=lambda: None,
        status_mapper=lambda status: status,
        logger=logger,
    )
    service = _FakeService(fail_times=1)
    transacao = SimpleNamespace(id=11)

    gateway.confirm_with_retry(
        service=service,
        transacao=transacao,
        retry_delays=(0.0, 0.0),
    )

    assert service.calls == 2
    assert len(logger.warnings) == 1
    assert logger.warnings[0]["message"] == "confirmar_pagamento_operational_error"


def test_confirm_with_retry_raises_last_operational_error():
    logger = _FakeLogger()
    gateway = DjangoPaymentConfirmationGateway(
        payment_model_getter=lambda: None,
        status_mapper=lambda status: status,
        logger=logger,
    )
    service = _FakeService(fail_times=3)
    transacao = SimpleNamespace(id=12)

    with pytest.raises(OperationalError):
        gateway.confirm_with_retry(
            service=service,
            transacao=transacao,
            retry_delays=(0.0, 0.0),
        )

    assert service.calls == 2
    assert len(logger.warnings) == 2


def test_sync_payment_model_updates_transacao_fields():
    logger = _FakeLogger()
    pagamento = SimpleNamespace(
        status="approved",
        transaction_id="external-123",
        token="tok_abc",
    )
    payment_model = SimpleNamespace(
        objects=SimpleNamespace(
            filter=lambda pk: SimpleNamespace(first=lambda: pagamento),
        )
    )
    gateway = DjangoPaymentConfirmationGateway(
        payment_model_getter=lambda: payment_model,
        status_mapper=lambda status: "approved" if status == "approved" else status,
        logger=logger,
    )
    transacao = _FakeTransacao()

    gateway.sync_payment_model(transacao=transacao)

    assert transacao.status == "approved"
    assert transacao.external_id == "external-123"
    assert transacao.detalhes["payment_status"] == "approved"
    assert transacao.detalhes["payment_token"] == "tok_abc"
    assert "status" in transacao.saved_update_fields
    assert "external_id" in transacao.saved_update_fields
    assert "detalhes" in transacao.saved_update_fields
    assert "atualizado_em" in transacao.saved_update_fields

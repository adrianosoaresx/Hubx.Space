import hmac
import json
import os
from decimal import Decimal
from hashlib import sha256

import django
import pytest
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from organizacoes.models import Organizacao
from pagamentos.models import Pedido, Transacao
from pagamentos.views import WebhookView


@pytest.mark.django_db
def test_webhook_mercadopago_transacao_conhecida_confirma_com_stub(monkeypatch):
    org = Organizacao.objects.create(nome="Org Webhook Known", cnpj="12345678009995")
    pedido = Pedido.objects.create(
        organizacao=org,
        valor=Decimal("120.00"),
        status=Pedido.Status.PENDENTE,
    )
    transacao = Transacao.objects.create(
        pedido=pedido,
        metodo=Transacao.Metodo.PIX,
        valor=Decimal("120.00"),
        status=Transacao.Status.PENDENTE,
        external_id="known-smoke-001",
    )

    def _fake_confirm_retry(self, service, tx):
        tx.status = Transacao.Status.APROVADA
        tx.save(update_fields=["status", "atualizado_em"])

    monkeypatch.setattr(WebhookView, "_confirmar_pagamento_com_retry", _fake_confirm_retry)
    monkeypatch.setenv("MERCADO_PAGO_WEBHOOK_SECRET", "known-secret")

    payload = {"data": {"id": "known-smoke-001"}}
    raw = json.dumps(payload).encode("utf-8")
    signature = hmac.new(b"known-secret", msg=raw, digestmod=sha256).hexdigest()

    client = Client()
    response = client.post(
        "/pagamentos/webhook/mercadopago/",
        data=raw,
        content_type="application/json",
        HTTP_X_SIGNATURE=signature,
    )

    transacao.refresh_from_db()
    assert response.status_code == 200
    assert transacao.status == Transacao.Status.APROVADA

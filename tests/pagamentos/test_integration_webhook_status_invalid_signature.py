import hmac
import json
import os
from decimal import Decimal
from hashlib import sha256

import django
import pytest
from django.test import Client
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from organizacoes.models import Organizacao  # noqa: E402
from pagamentos.models import Pedido, Transacao  # noqa: E402


@pytest.mark.django_db
def test_webhook_invalid_signature_keeps_pending_status_and_no_hx_redirect(monkeypatch):
    monkeypatch.setenv("MERCADO_PAGO_WEBHOOK_SECRET", "expected-secret")

    organizacao = Organizacao.objects.create(nome="Org WH Invalid", cnpj="12345678000994")
    pedido = Pedido.objects.create(
        organizacao=organizacao,
        valor=Decimal("150.00"),
        status=Pedido.Status.PENDENTE,
        email="wh.invalid@example.com",
        nome="Webhook Invalid",
    )
    transacao = Transacao.objects.create(
        pedido=pedido,
        metodo=Transacao.Metodo.PIX,
        valor=Decimal("150.00"),
        status=Transacao.Status.PENDENTE,
        external_id="wh-invalid-001",
    )

    payload = {"data": {"id": "wh-invalid-001"}}
    raw = json.dumps(payload).encode("utf-8")
    wrong_signature = hmac.new(b"wrong-secret", msg=raw, digestmod=sha256).hexdigest()

    client = Client()
    webhook_response = client.post(
        "/pagamentos/webhook/mercadopago/",
        data=raw,
        content_type="application/json",
        HTTP_X_SIGNATURE=wrong_signature,
    )
    assert webhook_response.status_code == 403

    transacao.refresh_from_db()
    assert transacao.status == Transacao.Status.PENDENTE

    status_response = client.get(
        reverse("pagamentos:status", kwargs={"pk": transacao.pk}),
        HTTP_HX_REQUEST="true",
    )
    assert status_response.status_code == 200
    assert "HX-Redirect" not in status_response.headers
    assert "Aguardando confirmação" in status_response.content.decode("utf-8")

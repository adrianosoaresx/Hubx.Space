import hmac
import json
import os
from hashlib import sha256

import django
import pytest
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()


@pytest.mark.django_db
def test_webhook_mercadopago_invalid_signature_returns_403(monkeypatch):
    monkeypatch.setenv("MERCADO_PAGO_WEBHOOK_SECRET", "expected-secret")

    payload = {"data": {"id": "external-unknown-1"}}
    raw = json.dumps(payload).encode("utf-8")
    wrong_signature = hmac.new(b"wrong-secret", msg=raw, digestmod=sha256).hexdigest()

    client = Client()
    response = client.post(
        "/pagamentos/webhook/mercadopago/",
        data=raw,
        content_type="application/json",
        HTTP_X_SIGNATURE=wrong_signature,
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_webhook_mercadopago_unknown_transaction_returns_200(monkeypatch):
    monkeypatch.setenv("MERCADO_PAGO_WEBHOOK_SECRET", "expected-secret")

    payload = {"data": {"id": "external-unknown-2"}}
    raw = json.dumps(payload).encode("utf-8")
    signature = hmac.new(b"expected-secret", msg=raw, digestmod=sha256).hexdigest()

    client = Client()
    response = client.post(
        "/pagamentos/webhook/mercadopago/",
        data=raw,
        content_type="application/json",
        HTTP_X_SIGNATURE=signature,
    )

    assert response.status_code == 200

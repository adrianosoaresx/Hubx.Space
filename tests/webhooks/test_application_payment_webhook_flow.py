import hmac
import os
from hashlib import sha256

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.webhooks.application.payment_webhook_flow import (
    extract_external_id,
    parse_webhook_payload,
    resolve_signature_secret,
    validate_hmac_signature,
)


def test_parse_webhook_payload_retorna_dict_vazio_em_json_invalido():
    assert parse_webhook_payload(b"{invalido") == {}


def test_parse_webhook_payload_retorna_payload_quando_json_valido():
    payload = parse_webhook_payload(b'{"data":{"id":"123"}}')
    assert payload == {"data": {"id": "123"}}


def test_extract_external_id_prioriza_data_id():
    payload = {"data": {"id": "abc"}, "id": "def", "resource": {"id": "ghi"}}
    assert extract_external_id(payload) == "abc"


def test_extract_external_id_usa_resource_id_como_fallback():
    payload = {"resource": {"id": "ghi"}}
    assert extract_external_id(payload) == "ghi"


def test_resolve_signature_secret_prioriza_secret_da_organizacao(monkeypatch):
    monkeypatch.setenv("MERCADO_PAGO_WEBHOOK_SECRET", "secret-env")
    assert (
        resolve_signature_secret("secret-org", "MERCADO_PAGO_WEBHOOK_SECRET")
        == "secret-org"
    )


def test_resolve_signature_secret_usa_env_quando_org_nao_definida(monkeypatch):
    monkeypatch.setenv("MERCADO_PAGO_WEBHOOK_SECRET", "secret-env")
    assert (
        resolve_signature_secret(None, "MERCADO_PAGO_WEBHOOK_SECRET")
        == "secret-env"
    )


def test_validate_hmac_signature_retorna_true_sem_secret():
    assert validate_hmac_signature(
        raw_body=b'{"id":1}', provided_signature=None, secret=None
    )


def test_validate_hmac_signature_retorna_false_sem_header_quando_secret_existe():
    assert not validate_hmac_signature(
        raw_body=b'{"id":1}', provided_signature=None, secret="secret"
    )


def test_validate_hmac_signature_retorna_true_quando_assinatura_confere():
    raw_body = b'{"id":"123"}'
    secret = "secret"
    signature = hmac.new(secret.encode(), msg=raw_body, digestmod=sha256).hexdigest()

    assert validate_hmac_signature(
        raw_body=raw_body, provided_signature=signature, secret=secret
    )


def test_validate_hmac_signature_retorna_false_quando_assinatura_invalida():
    assert not validate_hmac_signature(
        raw_body=b'{"id":"123"}',
        provided_signature="assinatura-invalida",
        secret="secret",
    )

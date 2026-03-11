import os
from types import SimpleNamespace

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.pagamentos.application.payment_webhook_orchestration import (  # noqa: E402
    execute_payment_webhook_orchestration,
)


def test_webhook_orchestration_missing_external_id():
    result = execute_payment_webhook_orchestration(
        raw_body=b"{}",
        provided_signature="sig",
        parse_payload=lambda _: {},
        extract_external_id=lambda payload: "",
        find_transaction_by_external_id=lambda external_id: None,
        resolve_organizacao=lambda payload, transacao: None,
        is_signature_valid=lambda raw, sig, org: True,
        confirm_known_transaction=lambda org, tx: None,
        update_known_transaction=lambda tx: None,
    )

    assert result.http_status == 400
    assert result.reason == "missing_external_id"


def test_webhook_orchestration_invalid_signature():
    result = execute_payment_webhook_orchestration(
        raw_body=b'{"data":{"id":"abc"}}',
        provided_signature="bad",
        parse_payload=lambda _: {"data": {"id": "abc"}},
        extract_external_id=lambda payload: payload["data"]["id"],
        find_transaction_by_external_id=lambda external_id: SimpleNamespace(id=1),
        resolve_organizacao=lambda payload, transacao: None,
        is_signature_valid=lambda raw, sig, org: False,
        confirm_known_transaction=lambda org, tx: None,
        update_known_transaction=lambda tx: None,
    )

    assert result.http_status == 403
    assert result.reason == "invalid_signature"


def test_webhook_orchestration_known_transaction():
    calls = {"confirmed": 0, "updated": 0}

    def _confirm(org, tx):
        calls["confirmed"] += 1

    def _update(tx):
        calls["updated"] += 1

    result = execute_payment_webhook_orchestration(
        raw_body=b'{"data":{"id":"abc"}}',
        provided_signature="sig",
        parse_payload=lambda _: {"data": {"id": "abc"}},
        extract_external_id=lambda payload: payload["data"]["id"],
        find_transaction_by_external_id=lambda external_id: SimpleNamespace(id=1, external_id=external_id),
        resolve_organizacao=lambda payload, transacao: None,
        is_signature_valid=lambda raw, sig, org: True,
        confirm_known_transaction=_confirm,
        update_known_transaction=_update,
    )

    assert result.http_status == 200
    assert result.reason == "processed_known_transaction"
    assert calls["confirmed"] == 1
    assert calls["updated"] == 1

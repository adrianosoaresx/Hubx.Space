from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping


@dataclass(frozen=True)
class PaymentWebhookResult:
    http_status: int
    reason: str
    external_id: str | None
    has_known_transaction: bool


def execute_payment_webhook_orchestration(
    *,
    raw_body: bytes,
    provided_signature: str | None,
    parse_payload: Callable[[bytes], dict[str, Any]],
    extract_external_id: Callable[[Mapping[str, Any]], str],
    find_transaction_by_external_id: Callable[[str], Any | None],
    resolve_organizacao: Callable[[dict[str, Any], Any | None], Any | None],
    is_signature_valid: Callable[[bytes, str | None, Any | None], bool],
    confirm_known_transaction: Callable[[Any | None, Any], None],
    update_known_transaction: Callable[[Any], None],
) -> PaymentWebhookResult:
    payload = parse_payload(raw_body)
    external_id = str(extract_external_id(payload) or "").strip()
    if not external_id:
        return PaymentWebhookResult(
            http_status=400,
            reason="missing_external_id",
            external_id=None,
            has_known_transaction=False,
        )

    transacao = find_transaction_by_external_id(external_id)
    organizacao = resolve_organizacao(payload, transacao)
    if not is_signature_valid(raw_body, provided_signature, organizacao):
        return PaymentWebhookResult(
            http_status=403,
            reason="invalid_signature",
            external_id=external_id,
            has_known_transaction=transacao is not None,
        )

    if transacao is None:
        return PaymentWebhookResult(
            http_status=200,
            reason="unknown_transaction",
            external_id=external_id,
            has_known_transaction=False,
        )

    confirm_known_transaction(organizacao, transacao)
    update_known_transaction(transacao)
    return PaymentWebhookResult(
        http_status=200,
        reason="processed_known_transaction",
        external_id=external_id,
        has_known_transaction=True,
    )

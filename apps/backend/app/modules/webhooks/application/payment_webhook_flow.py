from __future__ import annotations

import hmac
import json
import os
from hashlib import sha256
from typing import Any, Mapping


def parse_webhook_payload(raw_body: bytes) -> dict[str, Any]:
    try:
        return json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}


def extract_external_id(payload: Mapping[str, Any]) -> str:
    data = payload.get("data", {}) if isinstance(payload.get("data"), dict) else {}
    resource = payload.get("resource", {}) if isinstance(payload.get("resource"), dict) else {}
    return str(data.get("id") or payload.get("id", "") or resource.get("id", ""))


def resolve_signature_secret(
    organization_secret: str | None, env_var_name: str
) -> str | None:
    return organization_secret or os.getenv(env_var_name)


def validate_hmac_signature(
    *,
    raw_body: bytes,
    provided_signature: str | None,
    secret: str | None,
) -> bool:
    if not secret:
        return True
    if not provided_signature:
        return False
    expected_signature = hmac.new(secret.encode(), msg=raw_body, digestmod=sha256).hexdigest()
    return hmac.compare_digest(provided_signature, expected_signature)

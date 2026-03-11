from __future__ import annotations

from typing import Any, Mapping


_SENSITIVE_KEYS = {"password", "token", "cpf", "secret"}


def normalize_audit_status(status: str | None) -> str:
    value = (status or "").strip().upper()
    if value in {"SUCCESS", "OK"}:
        return "SUCCESS"
    if value in {"FAILURE", "FAILED", "ERROR"}:
        return "FAILURE"
    return "SUCCESS"


def status_from_http_code(status_code: int) -> str:
    return "SUCCESS" if 200 <= status_code < 400 else "FAILURE"


def severity_from_status(status: str) -> str:
    return "high" if normalize_audit_status(status) == "FAILURE" else "info"


def build_audit_action(method: str, path: str) -> str:
    return f"{(method or '').upper()}:{path}"


def sanitize_metadata(data: Mapping[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, value in data.items():
        if key.lower() in _SENSITIVE_KEYS:
            continue
        if isinstance(value, Mapping):
            sanitized[key] = sanitize_metadata(value)
            continue
        if isinstance(value, list):
            sanitized[key] = [
                sanitize_metadata(item) if isinstance(item, Mapping) else item for item in value
            ]
            continue
        sanitized[key] = value
    return sanitized


def enrich_metadata(
    metadata: Mapping[str, Any] | None,
    *,
    status: str,
) -> dict[str, Any]:
    base = sanitize_metadata(metadata or {})
    base.setdefault("severity", severity_from_status(status))
    return base

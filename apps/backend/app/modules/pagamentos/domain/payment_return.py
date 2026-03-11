from __future__ import annotations

VALID_RETURN_STATUSES = frozenset({"sucesso", "falha", "pendente"})


def normalize_return_status(raw_status: str | None) -> str | None:
    status = (raw_status or "").strip().lower()
    if status in VALID_RETURN_STATUSES:
        return status
    return None

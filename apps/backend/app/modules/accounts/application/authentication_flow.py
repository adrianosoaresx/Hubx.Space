from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Pending2FASessionData:
    user_id: int
    next_url: str | None
    method: str | None


def build_pending_2fa_session_data(*, user_id: int, next_url: str | None, method: str | None) -> Pending2FASessionData:
    return Pending2FASessionData(
        user_id=user_id,
        next_url=next_url,
        method=method,
    )


def resolve_2fa_success_redirect(
    *,
    explicit_next_url: str | None,
    session_next_url: str | None,
    fallback_url: str,
) -> str:
    return explicit_next_url or session_next_url or fallback_url

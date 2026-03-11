from __future__ import annotations


def is_token_invalid_or_expired(*, token, now) -> bool:
    return bool(token.used_at) or token.expires_at < now

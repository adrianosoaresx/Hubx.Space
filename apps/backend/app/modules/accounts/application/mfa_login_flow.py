from __future__ import annotations


def resolve_switch_method(*, post_data, available_methods: list[str]) -> str | None:
    switch_method = (post_data.get("switch_method") or "").strip()
    if switch_method in available_methods:
        return switch_method
    return None


def is_resend_email_action(*, method: str, action: str, email_otp_method: str) -> bool:
    return method == email_otp_method and action == "resend_email_code"

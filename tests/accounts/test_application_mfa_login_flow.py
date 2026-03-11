import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.accounts.application.mfa_login_flow import (  # noqa: E402
    is_resend_email_action,
    resolve_switch_method,
)


def test_resolve_switch_method_returns_valid_method():
    method = resolve_switch_method(
        post_data={"switch_method": "email_otp"},
        available_methods=["totp", "email_otp"],
    )
    assert method == "email_otp"


def test_resolve_switch_method_returns_none_when_invalid():
    method = resolve_switch_method(
        post_data={"switch_method": "sms"},
        available_methods=["totp", "email_otp"],
    )
    assert method is None


def test_is_resend_email_action_true_for_email_otp():
    assert is_resend_email_action(
        method="email_otp",
        action="resend_email_code",
        email_otp_method="email_otp",
    )

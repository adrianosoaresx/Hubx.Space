import os
from types import SimpleNamespace

import django
import pyotp
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from tokens.models import TOTPDevice  # noqa: E402

User = get_user_model()


def _fake_challenge(pk_value: str):
    return SimpleNamespace(pk=pk_value)


@pytest.mark.django_db
def test_login_totp_switch_method_to_email_otp(monkeypatch):
    secret = pyotp.random_base32()
    user = User.objects.create_user(
        username="switch.mfa",
        email="switch@example.com",
        password="senha123forte",
        two_factor_enabled=True,
        two_factor_secret=secret,
        two_factor_email_enabled=True,
    )
    TOTPDevice.objects.create(usuario=user, secret=secret, confirmado=True)

    monkeypatch.setattr(
        "accounts.views.issue_email_challenge",
        lambda **kwargs: _fake_challenge("11111111-1111-1111-1111-111111111111"),
    )

    client = Client()
    login_response = client.post(
        reverse("accounts:login"),
        {"email": user.email, "password": "senha123forte"},
    )
    assert login_response.status_code == 302
    assert login_response.url == reverse("accounts:login_totp")

    switch_response = client.post(
        reverse("accounts:login_totp"),
        {"switch_method": "email_otp"},
    )
    assert switch_response.status_code == 302
    assert switch_response.url == reverse("accounts:login_totp")

    session = client.session
    assert session.get("pending_2fa_method") == "email_otp"
    assert session.get("pending_2fa_challenge_id") == "11111111-1111-1111-1111-111111111111"


@pytest.mark.django_db
def test_login_totp_resend_email_code_updates_challenge(monkeypatch):
    secret = pyotp.random_base32()
    user = User.objects.create_user(
        username="resend.mfa",
        email="resend@example.com",
        password="senha123forte",
        two_factor_enabled=True,
        two_factor_secret=secret,
        two_factor_email_enabled=True,
        two_factor_preferred_method="email_otp",
    )
    TOTPDevice.objects.create(usuario=user, secret=secret, confirmado=True)

    call_ids = iter(
        [
            "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        ]
    )

    monkeypatch.setattr(
        "accounts.views.issue_email_challenge",
        lambda **kwargs: _fake_challenge(next(call_ids)),
    )
    monkeypatch.setattr(
        "accounts.views.get_active_email_challenge",
        lambda **kwargs: _fake_challenge("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
    )

    client = Client()
    login_response = client.post(
        reverse("accounts:login"),
        {"email": user.email, "password": "senha123forte"},
    )
    assert login_response.status_code == 302
    assert login_response.url == reverse("accounts:login_totp")

    response = client.post(
        reverse("accounts:login_totp"),
        {"action": "resend_email_code"},
    )

    assert response.status_code == 200
    assert b"reenviado" in response.content.lower()
    session = client.session
    assert session.get("pending_2fa_challenge_id") == "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"

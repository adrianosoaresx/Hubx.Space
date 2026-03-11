import os

import django
import pyotp
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from accounts.models import SecurityEvent  # noqa: E402
from tokens.models import TOTPDevice  # noqa: E402

User = get_user_model()


@pytest.mark.django_db
def test_api_enable_2fa_invalid_password_logs_failure_event():
    user = User.objects.create_user(
        username="api.2fa.fail.enable",
        email="api.2fa.fail.enable@example.com",
        password="Senha12345!",
        is_active=True,
    )
    client = Client()
    client.force_login(user)

    response = client.post(
        reverse("accounts_api:account-enable-2fa"),
        data={"password": "senha-incorreta"},
        content_type="application/json",
    )

    assert response.status_code == 400
    assert SecurityEvent.objects.filter(
        usuario=user,
        evento="2fa_habilitacao_falha",
    ).exists()


@pytest.mark.django_db
def test_api_enable_2fa_success_logs_event_and_creates_device():
    user = User.objects.create_user(
        username="api.2fa.ok.enable",
        email="api.2fa.ok.enable@example.com",
        password="Senha12345!",
        is_active=True,
    )
    client = Client()
    client.force_login(user)

    first_step = client.post(
        reverse("accounts_api:account-enable-2fa"),
        data={"password": "Senha12345!"},
        content_type="application/json",
    )
    assert first_step.status_code == 200
    secret = first_step.json()["secret"]

    second_step = client.post(
        reverse("accounts_api:account-enable-2fa"),
        data={"password": "Senha12345!", "code": pyotp.TOTP(secret).now()},
        content_type="application/json",
    )

    user.refresh_from_db()
    assert second_step.status_code == 200
    assert user.two_factor_enabled is True
    assert TOTPDevice.all_objects.filter(usuario=user, confirmado=True).exists()
    assert SecurityEvent.objects.filter(
        usuario=user,
        evento="2fa_habilitado",
    ).exists()


@pytest.mark.django_db
def test_api_disable_2fa_invalid_password_logs_failure_event():
    secret = pyotp.random_base32()
    user = User.objects.create_user(
        username="api.2fa.fail.disable",
        email="api.2fa.fail.disable@example.com",
        password="Senha12345!",
        is_active=True,
        two_factor_enabled=True,
        two_factor_secret=secret,
    )
    TOTPDevice.objects.create(usuario=user, secret=secret, confirmado=True)
    client = Client()
    client.force_login(user)

    response = client.post(
        reverse("accounts_api:account-disable-2fa"),
        data={"password": "senha-incorreta", "code": "123456"},
        content_type="application/json",
    )

    assert response.status_code == 400
    assert SecurityEvent.objects.filter(
        usuario=user,
        evento="2fa_desabilitacao_falha",
    ).exists()


@pytest.mark.django_db
def test_api_disable_2fa_success_logs_event_and_removes_device():
    secret = pyotp.random_base32()
    user = User.objects.create_user(
        username="api.2fa.ok.disable",
        email="api.2fa.ok.disable@example.com",
        password="Senha12345!",
        is_active=True,
        two_factor_enabled=True,
        two_factor_secret=secret,
    )
    TOTPDevice.objects.create(usuario=user, secret=secret, confirmado=True)
    client = Client()
    client.force_login(user)

    response = client.post(
        reverse("accounts_api:account-disable-2fa"),
        data={"password": "Senha12345!", "code": pyotp.TOTP(secret).now()},
        content_type="application/json",
    )

    user.refresh_from_db()
    assert response.status_code == 200
    assert user.two_factor_enabled is False
    assert user.two_factor_secret in (None, "")
    assert not TOTPDevice.objects.filter(usuario=user).exists()
    assert SecurityEvent.objects.filter(
        usuario=user,
        evento="2fa_desabilitado",
    ).exists()

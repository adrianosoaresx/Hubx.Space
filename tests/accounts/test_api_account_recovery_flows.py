import os
from datetime import timedelta

import django
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from accounts.models import AccountToken, SecurityEvent  # noqa: E402
from audit.models import AuditLog  # noqa: E402

User = get_user_model()


@pytest.mark.django_db
def test_api_confirm_email_success():
    user = User.objects.create_user(
        username="confirm.user",
        email="confirm@example.com",
        password="Senha12345!",
        is_active=False,
        email_confirmed=False,
    )
    token = AccountToken.objects.create(
        usuario=user,
        tipo=AccountToken.Tipo.EMAIL_CONFIRMATION,
        expires_at=timezone.now() + timedelta(hours=1),
    )
    client = Client()

    response = client.post(
        reverse("accounts_api:account-confirm-email"),
        data={"token": token.codigo},
        content_type="application/json",
    )
    user.refresh_from_db()

    assert response.status_code == 200
    assert response.json()["detail"]
    assert user.is_active is True
    assert user.email_confirmed is True


@pytest.mark.django_db
def test_api_request_password_reset_missing_email_returns_400():
    client = Client()

    response = client.post(
        reverse("accounts_api:account-request-password-reset"),
        data={},
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "detail" in response.json()


@pytest.mark.django_db
def test_api_reset_password_invalid_token_returns_400():
    client = Client()

    response = client.post(
        reverse("accounts_api:account-reset-password"),
        data={"token": "token-invalido", "password": "SenhaNova123!"},
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "detail" in response.json()


@pytest.mark.django_db
def test_api_reset_password_success():
    user = User.objects.create_user(
        username="reset.user",
        email="reset@example.com",
        password="SenhaAntiga123!",
        is_active=True,
    )
    token = AccountToken.objects.create(
        usuario=user,
        tipo=AccountToken.Tipo.PASSWORD_RESET,
        expires_at=timezone.now() + timedelta(hours=1),
    )
    client = Client()

    response = client.post(
        reverse("accounts_api:account-reset-password"),
        data={"token": token.codigo, "password": "SenhaNova123!"},
        content_type="application/json",
    )
    user.refresh_from_db()
    token.refresh_from_db()

    assert response.status_code == 200
    assert user.check_password("SenhaNova123!")
    assert token.used_at is not None


@pytest.mark.django_db
def test_api_cancel_delete_missing_token_returns_400():
    client = Client()

    response = client.post(
        reverse("accounts_api:account-cancel-delete"),
        data={},
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "detail" in response.json()


@pytest.mark.django_db
def test_api_cancel_delete_success_reactivates_user():
    user = User.objects.create_user(
        username="api.cancel.user",
        email="api.cancel@example.com",
        password="Senha12345!",
        is_active=False,
        deleted=True,
        exclusao_confirmada=True,
    )
    token = AccountToken.objects.create(
        usuario=user,
        tipo=AccountToken.Tipo.CANCEL_DELETE,
        expires_at=timezone.now() + timedelta(hours=1),
    )
    client = Client()

    response = client.post(
        reverse("accounts_api:account-cancel-delete"),
        data={"token": token.codigo},
        content_type="application/json",
    )
    user.refresh_from_db()
    token.refresh_from_db()

    assert response.status_code == 200
    assert response.json()["detail"]
    assert user.deleted is False
    assert user.is_active is True
    assert user.exclusao_confirmada is False
    assert token.used_at is not None
    assert AuditLog.objects.filter(
        user=user,
        action="account_delete_canceled",
        object_type="User",
        object_id=str(user.id),
    ).exists()


@pytest.mark.django_db
def test_api_delete_me_invalid_confirmation_returns_400():
    user = User.objects.create_user(
        username="api.delete.invalid",
        email="api.delete.invalid@example.com",
        password="Senha12345!",
        is_active=True,
    )
    client = Client()
    client.force_login(user)

    response = client.delete(
        reverse("accounts_api:account-delete-me"),
        data={"confirm": "NAO"},
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "detail" in response.json()
    assert SecurityEvent.objects.filter(
        usuario=user,
        evento="conta_exclusao_falha",
    ).exists()


@pytest.mark.django_db
def test_api_delete_me_success_issues_cancel_token():
    user = User.objects.create_user(
        username="api.delete.ok",
        email="api.delete.ok@example.com",
        password="Senha12345!",
        is_active=True,
    )
    client = Client()
    client.force_login(user)

    response = client.delete(
        reverse("accounts_api:account-delete-me"),
        data={"confirm": "EXCLUIR"},
        content_type="application/json",
    )

    assert response.status_code == 204

    user_from_all = User.all_objects.get(pk=user.pk)
    assert user_from_all.deleted is True
    assert user_from_all.is_active is False
    assert user_from_all.exclusao_confirmada is True
    assert AccountToken.objects.filter(
        usuario=user_from_all,
        tipo=AccountToken.Tipo.CANCEL_DELETE,
    ).exists()

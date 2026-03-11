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

from accounts.models import AccountToken  # noqa: E402

User = get_user_model()


@pytest.mark.django_db
def test_confirmar_email_view_success():
    user = User.objects.create_user(
        username="web.confirm.user",
        email="web.confirm@example.com",
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

    response = client.get(reverse("accounts:confirmar_email", args=[token.codigo]))
    user.refresh_from_db()

    assert response.status_code == 200
    assert user.is_active is True
    assert user.email_confirmed is True


@pytest.mark.django_db
def test_password_reset_confirm_invalid_token_returns_404():
    client = Client()

    response = client.get(reverse("accounts:password_reset_confirm", args=["invalido"]))

    assert response.status_code == 404


@pytest.mark.django_db
def test_password_reset_confirm_valid_get_marks_confirmed():
    user = User.objects.create_user(
        username="web.reset.user",
        email="web.reset@example.com",
        password="Senha12345!",
        is_active=True,
    )
    token = AccountToken.objects.create(
        usuario=user,
        tipo=AccountToken.Tipo.PASSWORD_RESET,
        expires_at=timezone.now() + timedelta(hours=1),
        status=AccountToken.Status.PENDENTE,
    )
    client = Client()

    response = client.get(reverse("accounts:password_reset_confirm", args=[token.codigo]))
    token.refresh_from_db()

    assert response.status_code == 200
    assert token.status == AccountToken.Status.CONFIRMADO


@pytest.mark.django_db
def test_cancel_delete_view_success_reactivates_user():
    user = User.objects.create_user(
        username="web.cancel.user",
        email="web.cancel@example.com",
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

    response = client.get(reverse("accounts:cancel_delete", args=[token.codigo]))
    user.refresh_from_db()
    token.refresh_from_db()

    assert response.status_code == 200
    assert response.context["status"] == "sucesso"
    assert user.deleted is False
    assert user.is_active is True
    assert user.exclusao_confirmada is False
    assert token.used_at is not None


@pytest.mark.django_db
def test_cancel_delete_view_invalid_token_renders_error():
    client = Client()

    response = client.get(reverse("accounts:cancel_delete", args=["invalido"]))

    assert response.status_code == 200
    assert response.context["status"] == "erro"

import os

import django
import pytest
from django.test import Client
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from accounts.factories import UserFactory  # noqa: E402
from nucleos.factories import NucleoFactory  # noqa: E402
from organizacoes.factories import OrganizacaoFactory  # noqa: E402


@pytest.mark.django_db
def test_deactivate_user_view_htmx_returns_info_partial():
    organizacao = OrganizacaoFactory()
    nucleo = NucleoFactory(organizacao=organizacao)
    admin_user = UserFactory(
        user_type="admin",
        organizacao=organizacao,
        nucleo_obj=nucleo,
    )
    target_user = UserFactory(
        user_type="nucleado",
        organizacao=organizacao,
        nucleo_obj=nucleo,
        is_active=True,
    )
    client = Client()
    client.force_login(admin_user)

    response = client.post(
        reverse("accounts:deactivate_user"),
        {"public_id": str(target_user.public_id), "username": target_user.username},
        HTTP_HX_REQUEST="true",
    )

    target_user.refresh_from_db()
    assert response.status_code == 200
    assert target_user.is_active is False
    assert b"perfil-info-accordion" in response.content


@pytest.mark.django_db
def test_account_api_activate_and_deactivate_success():
    organizacao = OrganizacaoFactory()
    nucleo = NucleoFactory(organizacao=organizacao)
    admin_user = UserFactory(
        user_type="admin",
        organizacao=organizacao,
        nucleo_obj=nucleo,
    )
    target_user = UserFactory(
        user_type="nucleado",
        organizacao=organizacao,
        nucleo_obj=nucleo,
        is_active=True,
    )
    client = Client()
    client.force_login(admin_user)

    deactivate_response = client.post(
        reverse("accounts_api:account-deactivate", args=[target_user.pk]),
        content_type="application/json",
    )
    target_user.refresh_from_db()
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False
    assert target_user.is_active is False

    activate_response = client.post(
        reverse("accounts_api:account-activate", args=[target_user.pk]),
        content_type="application/json",
    )
    target_user.refresh_from_db()
    assert activate_response.status_code == 200
    assert activate_response.json()["is_active"] is True
    assert target_user.is_active is True


@pytest.mark.django_db
def test_account_api_deactivate_forbidden_for_different_org():
    admin_org = OrganizacaoFactory()
    target_org = OrganizacaoFactory()
    admin_nucleo = NucleoFactory(organizacao=admin_org)
    target_nucleo = NucleoFactory(organizacao=target_org)
    admin_user = UserFactory(
        user_type="admin",
        organizacao=admin_org,
        nucleo_obj=admin_nucleo,
    )
    target_user = UserFactory(
        user_type="nucleado",
        organizacao=target_org,
        nucleo_obj=target_nucleo,
        is_active=True,
    )
    client = Client()
    client.force_login(admin_user)

    response = client.post(
        reverse("accounts_api:account-deactivate", args=[target_user.pk]),
        content_type="application/json",
    )

    assert response.status_code == 403
    assert "detail" in response.json()

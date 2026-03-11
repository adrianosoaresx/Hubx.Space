import os

import django
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from organizacoes.models import Organizacao  # noqa: E402

User = get_user_model()


@pytest.mark.django_db
def test_api_rate_user_returns_aggregated_payload(monkeypatch):
    organizacao = Organizacao.objects.create(nome="Org Rating API", cnpj="12345678000991")
    rated_user = User.objects.create_user(
        username="rated.user.api",
        email="rated.user.api@example.com",
        password="Senha12345!",
        organizacao=organizacao,
    )
    rater_user = User.objects.create_user(
        username="rater.user.api",
        email="rater.user.api@example.com",
        password="Senha12345!",
        organizacao=organizacao,
    )

    monkeypatch.setattr(type(rater_user), "has_perm", lambda self, perm: True)

    client = Client()
    client.force_login(rater_user)

    response = client.post(
        reverse("accounts_api:account-rate-user", kwargs={"pk": rated_user.pk}),
        data={"score": 5, "comment": "Excelente"},
        content_type="application/json",
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["average"] == 5.0
    assert payload["display"] == "5,0"
    assert payload["total"] == 1

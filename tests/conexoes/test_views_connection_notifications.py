from __future__ import annotations

import os

import django
import pytest
from django.contrib.auth import get_user_model
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from accounts.models import UserType
from organizacoes.models import Organizacao

User = get_user_model()


def _create_org() -> Organizacao:
    return Organizacao.objects.create(
        nome=f"Org Conexoes {Organizacao.objects.count()}",
        cnpj=f"55667788{Organizacao.objects.count() + 1000:04d}95",
    )


def _create_user(org: Organizacao, username: str):
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="senha123",
        user_type=UserType.NUCLEADO,
        organizacao=org,
    )


@pytest.mark.django_db
def test_solicitar_conexao_dispara_template_request(monkeypatch):
    org = _create_org()
    usuario = _create_user(org, "con_user_a")
    alvo = _create_user(org, "con_user_b")
    dispatched = {}

    class _FakeTask:
        @staticmethod
        def delay(user_id: str, template_codigo: str, context: dict[str, str]):
            dispatched["user_id"] = user_id
            dispatched["template_codigo"] = template_codigo
            dispatched["context"] = context

    monkeypatch.setattr("conexoes.views.enviar_notificacao_conexao_async", _FakeTask)

    client = Client()
    client.force_login(usuario)
    response = client.post(f"/conexoes/perfil/conexoes/{alvo.id}/solicitar/")

    assert response.status_code == 302
    assert dispatched["user_id"] == str(alvo.id)
    assert dispatched["template_codigo"] == "connection_request"
    assert dispatched["context"]["actor_id"] == str(usuario.id)
    assert "solicitante" in dispatched["context"]


@pytest.mark.django_db
def test_aceitar_conexao_dispara_template_accepted(monkeypatch):
    org = _create_org()
    usuario = _create_user(org, "con_user_c")
    solicitante = _create_user(org, "con_user_d")
    usuario.followers.add(solicitante)
    dispatched = {}

    class _FakeTask:
        @staticmethod
        def delay(user_id: str, template_codigo: str, context: dict[str, str]):
            dispatched["user_id"] = user_id
            dispatched["template_codigo"] = template_codigo
            dispatched["context"] = context

    monkeypatch.setattr("conexoes.views.enviar_notificacao_conexao_async", _FakeTask)

    client = Client()
    client.force_login(usuario)
    response = client.post(f"/conexoes/perfil/conexoes/{solicitante.id}/aceitar/")

    assert response.status_code == 302
    assert dispatched["user_id"] == str(solicitante.id)
    assert dispatched["template_codigo"] == "connection_accepted"
    assert dispatched["context"]["actor_id"] == str(usuario.id)
    assert "solicitado" in dispatched["context"]

from __future__ import annotations

import os
import uuid

import django
import pytest
from django.contrib.auth import get_user_model
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from accounts.models import UserType
from notificacoes.models import Canal, NotificationLog, NotificationStatus, NotificationTemplate
from organizacoes.models import Organizacao

User = get_user_model()


def _create_user_with_org(username: str):
    org = Organizacao.objects.create(
        nome=f"Org {username}",
        cnpj=f"98765432{Organizacao.objects.count() + 1000:04d}95",
    )
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="senha123",
        user_type=UserType.NUCLEADO,
        organizacao=org,
    )


@pytest.mark.django_db
def test_notifications_dropdown_resolve_links_feed_e_connection():
    user = _create_user_with_org("notif_user")
    feed_template, _ = NotificationTemplate.objects.get_or_create(
        codigo="feed_like",
        defaults={
            "assunto": "Feed",
            "corpo": "Corpo",
            "canal": Canal.PUSH,
            "ativo": True,
        },
    )
    connection_template, _ = NotificationTemplate.objects.get_or_create(
        codigo="connection_request",
        defaults={
            "assunto": "Conexao",
            "corpo": "Corpo",
            "canal": Canal.PUSH,
            "ativo": True,
        },
    )

    NotificationLog.objects.create(
        user=user,
        template=feed_template,
        canal=Canal.APP,
        status=NotificationStatus.ENVIADA,
        context={"post_id": str(uuid.uuid4())},
    )
    NotificationLog.objects.create(
        user=user,
        template=connection_template,
        canal=Canal.APP,
        status=NotificationStatus.ENVIADA,
        context={"actor_id": 77},
    )

    client = Client()
    client.force_login(user)
    response = client.get("/notificacoes/minhas/dropdown/")

    assert response.status_code == 200
    html = response.content.decode("utf-8")
    assert "/feed/" in html
    assert "#post-" in html
    assert "/perfil/77" in html

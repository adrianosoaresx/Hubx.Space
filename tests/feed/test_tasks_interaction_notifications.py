from __future__ import annotations

import os

import django
import pytest
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from accounts.models import UserType
from feed.models import Post
from feed.tasks import notificar_autor_sobre_interacao
from organizacoes.models import Organizacao

User = get_user_model()


def _create_org() -> Organizacao:
    return Organizacao.objects.create(
        nome=f"Org Feed {Organizacao.objects.count()}",
        cnpj=f"66778899{Organizacao.objects.count() + 1000:04d}95",
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
def test_notificar_autor_sobre_interacao_envia_template_normalizado(monkeypatch):
    org = _create_org()
    autor = _create_user(org, "feed_author")
    post = Post.objects.create(
        autor=autor,
        organizacao=org,
        tipo_feed="global",
        conteudo="Post teste",
    )
    captured = {}

    def _fake_enviar_para_usuario(user, template_codigo, context):
        captured["user"] = user
        captured["template_codigo"] = template_codigo
        captured["context"] = context

    monkeypatch.setattr("feed.tasks.enviar_para_usuario", _fake_enviar_para_usuario)

    notificar_autor_sobre_interacao(str(post.id), "like")

    assert captured["user"] == autor
    assert captured["template_codigo"] == "feed_like"
    assert captured["context"] == {"post_id": str(post.id), "interaction_type": "like"}

import os
from types import SimpleNamespace

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.eventos.application.public_invite_flow import (
    build_login_redirect_url,
    build_public_invite_email_context,
    build_public_invite_email_subject,
    build_public_invite_info_context,
    build_public_invite_page_context,
    build_register_url,
)


def test_build_login_redirect_url():
    url = build_login_redirect_url(
        login_url="/accounts/login/",
        inscricao_url="/eventos/evento/1/inscricao/overview/",
    )
    assert url == "/accounts/login/?next=%2Feventos%2Fevento%2F1%2Finscricao%2Foverview%2F"


def test_build_register_url():
    url = build_register_url(
        token_url="/tokens/token/",
        evento_pk="abc-123",
        codigo="xyz",
    )
    assert url == "/tokens/token/?evento=abc-123&token=xyz"


def test_build_public_invite_email_context():
    evento = SimpleNamespace(titulo="Evento Teste")
    context = build_public_invite_email_context(
        evento=evento,
        codigo="COD",
        token_link="https://hubx.local/token",
    )
    assert context["evento"] is evento
    assert context["codigo"] == "COD"
    assert context["token_link"] == "https://hubx.local/token"


def test_build_public_invite_email_subject():
    subject = build_public_invite_email_subject(evento_titulo="Evento XPTO")
    assert subject == "Confirme sua inscrição em Evento XPTO"


def test_build_public_invite_info_context():
    convite = SimpleNamespace(id=10)
    evento = SimpleNamespace(id=20)
    context = build_public_invite_info_context(
        convite=convite,
        evento=evento,
        email="user@hubx.local",
        share_url="https://hubx.local/c/abc",
        register_url="/tokens/token/?evento=20&token=abc",
    )
    assert context["convite"] is convite
    assert context["evento"] is evento
    assert context["email"] == "user@hubx.local"


def test_build_public_invite_page_context():
    convite = SimpleNamespace(id=10)
    evento = SimpleNamespace(id=20)
    form = object()
    context = build_public_invite_page_context(
        convite=convite,
        evento=evento,
        inscricao_url="/eventos/evento/20/inscricao/overview/",
        share_url="https://hubx.local/c/abc",
        form=form,
    )
    assert context["convite"] is convite
    assert context["evento"] is evento
    assert context["inscricao_url"].endswith("/overview/")
    assert context["form"] is form

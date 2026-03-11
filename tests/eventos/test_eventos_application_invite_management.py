import os
from types import SimpleNamespace

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from accounts.models import UserType
from apps.backend.app.modules.eventos.application.invite_management import (
    build_convite_create_context,
    can_user_manage_convites,
)


def test_can_user_manage_convites_allowed_profiles():
    assert can_user_manage_convites(UserType.ADMIN.value) is True
    assert can_user_manage_convites(UserType.OPERADOR.value) is True
    assert can_user_manage_convites(UserType.COORDENADOR.value) is True


def test_can_user_manage_convites_denied_profiles():
    assert can_user_manage_convites(UserType.ASSOCIADO.value) is False
    assert can_user_manage_convites(UserType.NUCLEADO.value) is False


def test_build_convite_create_context():
    evento = SimpleNamespace(titulo="Evento XPTO")
    form = object()
    context = build_convite_create_context(
        evento=evento,
        form=form,
        back_href="/eventos/1/",
        fallback_url="/eventos/1/",
    )

    assert context["evento"] is evento
    assert context["form"] is form
    assert context["back_href"] == "/eventos/1/"
    assert context["cancel_component_config"]["href"] == "/eventos/1/"
    assert str(context["title"]) == "Novo convite"
    assert context["subtitle"] == "Evento XPTO"

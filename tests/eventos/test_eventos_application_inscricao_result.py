import os
from types import SimpleNamespace

import django
from django.test import RequestFactory

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.eventos.application.inscricao_result import (
    build_inscricao_result_context,
)


def test_build_inscricao_result_context():
    request = RequestFactory().get("/eventos/inscricoes/abc/resultado/")
    convite = SimpleNamespace(id=99)
    evento_id = "11111111-1111-1111-1111-111111111111"
    evento = SimpleNamespace(
        pk=evento_id,
        convites=SimpleNamespace(first=lambda: convite),
        get_absolute_url=lambda: f"/eventos/evento/{evento_id}/",
    )
    inscricao = SimpleNamespace(evento=evento)

    context = build_inscricao_result_context(
        request=request,
        inscricao=inscricao,
        status="success",
        message=None,
        title="Status da inscrição",
    )

    assert context["evento"] == evento
    assert context["inscricao"] == inscricao
    assert context["status"] == "success"
    assert context["convite"] == convite
    assert context["inscricao_url"].endswith(f"/evento/{evento_id}/inscricao/overview/")

import os
from types import SimpleNamespace

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.eventos.application.inscritos_reporting import (
    inscricao_sort_key,
    prepare_inscricoes_for_report,
    resolve_participante_nome,
)


def _inscricao(pk: int, contato: str = "", username: str = "user"):
    user = SimpleNamespace(
        contato=contato,
        display_name="",
        get_full_name=lambda: "",
        username=username,
    )
    return SimpleNamespace(pk=pk, user=user)


def test_resolve_participante_nome_prioriza_contato():
    inscricao = _inscricao(1, contato="Ana", username="ana_user")
    assert resolve_participante_nome(inscricao) == "Ana"


def test_inscricao_sort_key_usa_nome_normalizado():
    inscricao = _inscricao(2, contato="Bruno")
    assert inscricao_sort_key(inscricao) == ("bruno", 2)


def test_prepare_inscricoes_for_report_ordena_e_anota_nome():
    a = _inscricao(10, contato="Carlos")
    b = _inscricao(11, contato="Ana")
    result = prepare_inscricoes_for_report([a, b])

    assert [item.pk for item in result] == [11, 10]
    assert result[0].participante_nome == "Ana"

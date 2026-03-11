import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.eventos.application.day_listing import (
    build_eventos_por_dia_context,
    get_eventos_por_dia_template,
    parse_dia_iso,
    user_can_view_eventos_por_dia,
)


def test_parse_dia_iso_ok():
    dia, erro = parse_dia_iso("2026-03-10")

    assert erro is None
    assert str(dia) == "2026-03-10"


def test_parse_dia_iso_missing():
    dia, erro = parse_dia_iso(None)

    assert dia is None
    assert erro == "Parâmetro 'dia' obrigatório."


def test_parse_dia_iso_invalid():
    dia, erro = parse_dia_iso("10/03/2026")

    assert dia is None
    assert erro == "Data inválida."


def test_user_can_view_eventos_por_dia_root_false():
    assert user_can_view_eventos_por_dia("root") is False


def test_user_can_view_eventos_por_dia_admin_true():
    assert user_can_view_eventos_por_dia("admin") is True


def test_build_eventos_por_dia_context():
    dia, _ = parse_dia_iso("2026-03-10")
    context = build_eventos_por_dia_context(
        dia=dia,
        eventos=[{"id": 1}],
        title="Eventos",
        subtitle=None,
    )

    assert str(context["dia"]) == "2026-03-10"
    assert context["eventos"] == [{"id": 1}]
    assert context["title"] == "Eventos"
    assert context["subtitle"] is None


def test_get_eventos_por_dia_template():
    assert get_eventos_por_dia_template() == "eventos/partials/calendario/_lista_eventos_dia.html"

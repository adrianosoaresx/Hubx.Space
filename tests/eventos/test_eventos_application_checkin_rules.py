import os
from types import SimpleNamespace

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.eventos.application.checkin_rules import (
    build_checkin_form_context,
    build_checkin_success_payload,
    checkin_requires_post,
    is_inscricao_confirmada,
    user_can_access_checkin_form,
    user_can_execute_checkin,
    validate_checkin_codigo,
)


def test_user_can_access_checkin_form_owner_same_org():
    org = SimpleNamespace(id=1)
    user = SimpleNamespace(organizacao=org)
    inscricao = SimpleNamespace(user=user)
    evento = SimpleNamespace(organizacao=org)

    assert (
        user_can_access_checkin_form(
            evento=evento,
            user=user,
            inscricao=inscricao,
            tipo_usuario="associado",
        )
        is True
    )


def test_user_can_access_checkin_form_staff_same_org():
    org = SimpleNamespace(id=1)
    user = SimpleNamespace(organizacao=org)
    inscricao = SimpleNamespace(user=SimpleNamespace(organizacao=org))
    evento = SimpleNamespace(organizacao=org)

    assert (
        user_can_access_checkin_form(
            evento=evento,
            user=user,
            inscricao=inscricao,
            tipo_usuario="admin",
        )
        is True
    )


def test_user_can_access_checkin_form_false_different_org():
    user = SimpleNamespace(organizacao=SimpleNamespace(id=1))
    inscricao = SimpleNamespace(user=SimpleNamespace(organizacao=SimpleNamespace(id=2)))
    evento = SimpleNamespace(organizacao=SimpleNamespace(id=2))

    assert (
        user_can_access_checkin_form(
            evento=evento,
            user=user,
            inscricao=inscricao,
            tipo_usuario="admin",
        )
        is False
    )


def test_user_can_execute_checkin_same_org():
    org = SimpleNamespace(id=1)
    evento = SimpleNamespace(organizacao=org)
    user = SimpleNamespace(organizacao=org)
    assert user_can_execute_checkin(evento=evento, user=user) is True


def test_validate_checkin_codigo_ok_com_checksum():
    codigo = "inscricao:10:ck10"
    ok, erro = validate_checkin_codigo(
        codigo=codigo,
        inscricao_pk=10,
        checksum_generator=lambda raw: f"ck{raw}",
    )
    assert ok is True
    assert erro is None


def test_validate_checkin_codigo_falha_checksum():
    codigo = "inscricao:10:errado"
    ok, erro = validate_checkin_codigo(
        codigo=codigo,
        inscricao_pk=10,
        checksum_generator=lambda raw: f"ck{raw}",
    )
    assert ok is False
    assert erro == "Código inválido."


def test_checkin_requires_post():
    assert checkin_requires_post("POST") is True
    assert checkin_requires_post("GET") is False


def test_is_inscricao_confirmada():
    assert is_inscricao_confirmada("confirmada") is True
    assert is_inscricao_confirmada("pendente") is False


def test_build_checkin_form_context():
    evento = SimpleNamespace(descricao="Evento")
    inscricao = SimpleNamespace(id=10)
    context = build_checkin_form_context(
        evento=evento,
        inscricao=inscricao,
        title="Check-in",
        subtitle="Sub",
    )
    assert context["evento"] is evento
    assert context["inscricao"] is inscricao
    assert context["title"] == "Check-in"
    assert context["subtitle"] == "Sub"


def test_build_checkin_success_payload():
    assert build_checkin_success_payload(already_done=False) == {"status": "ok"}
    assert build_checkin_success_payload(already_done=True) == {
        "status": "ok",
        "message": "Check-in já realizado.",
    }

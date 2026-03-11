import os
from datetime import timedelta

import django
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.eventos.application.engagement_rules import (
    can_cancelar_inscricao,
    can_user_rate_event,
    parse_feedback_nota,
)


def test_can_user_rate_event_true():
    now = timezone.now()
    assert (
        can_user_rate_event(
            inscricao_confirmada=True,
            evento_data_fim=now - timedelta(minutes=1),
            now=now,
        )
        is True
    )


def test_can_user_rate_event_false_when_event_not_finished():
    now = timezone.now()
    assert (
        can_user_rate_event(
            inscricao_confirmada=True,
            evento_data_fim=now + timedelta(minutes=1),
            now=now,
        )
        is False
    )


def test_can_cancelar_inscricao_true():
    now = timezone.now()
    assert (
        can_cancelar_inscricao(
            inscricao_confirmada=True,
            inscricao_permitida=True,
            evento_data_inicio=now + timedelta(hours=2),
            pagamento_validado=False,
            now=now,
        )
        is True
    )


def test_can_cancelar_inscricao_false_when_pagamento_validado():
    now = timezone.now()
    assert (
        can_cancelar_inscricao(
            inscricao_confirmada=True,
            inscricao_permitida=True,
            evento_data_inicio=now + timedelta(hours=2),
            pagamento_validado=True,
            now=now,
        )
        is False
    )


def test_parse_feedback_nota_valid():
    nota, erro = parse_feedback_nota("5")
    assert nota == 5
    assert erro is None


def test_parse_feedback_nota_invalid():
    nota, erro = parse_feedback_nota("abc")
    assert nota is None
    assert erro == "Nota inválida."

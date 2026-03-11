import os
from decimal import Decimal
from types import SimpleNamespace

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.eventos.application.budget_rules import (
    apply_orcamento_changes,
    build_orcamento_success_payload,
    parse_orcamento_payload,
    should_persist_orcamento_changes,
    user_can_manage_evento_orcamento,
)


def test_user_can_manage_evento_orcamento_admin():
    assert user_can_manage_evento_orcamento("admin") is True


def test_user_can_manage_evento_orcamento_nucleado_false():
    assert user_can_manage_evento_orcamento("nucleado") is False


def test_parse_orcamento_payload_ok():
    dados, errors = parse_orcamento_payload({"orcamento_estimado": "10.50", "valor_gasto": "3"})

    assert errors == {}
    assert dados["orcamento_estimado"] == Decimal("10.50")
    assert dados["valor_gasto"] == Decimal("3")


def test_parse_orcamento_payload_invalid():
    dados, errors = parse_orcamento_payload({"orcamento_estimado": "abc"})

    assert dados == {}
    assert errors == {"orcamento_estimado": "valor inválido"}


def test_apply_orcamento_changes_only_changed_fields():
    evento = SimpleNamespace(orcamento_estimado=Decimal("100"), valor_gasto=Decimal("20"))

    alteracoes, update_fields = apply_orcamento_changes(
        evento,
        {"orcamento_estimado": Decimal("100"), "valor_gasto": Decimal("25")},
    )

    assert "orcamento_estimado" not in alteracoes
    assert alteracoes["valor_gasto"] == {"antes": "20.00", "depois": "25.00"}
    assert update_fields == ["valor_gasto"]


def test_should_persist_orcamento_changes():
    assert should_persist_orcamento_changes({"valor_gasto": {"antes": "1.00", "depois": "2.00"}}) is True
    assert should_persist_orcamento_changes({}) is False


def test_build_orcamento_success_payload():
    alteracoes = {"valor_gasto": {"antes": "1.00", "depois": "2.00"}}
    payload = build_orcamento_success_payload(alteracoes)
    assert payload == {"status": "ok", "alteracoes": alteracoes}

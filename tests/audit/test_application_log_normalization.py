import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.audit.application.log_normalization import (
    build_audit_action,
    enrich_metadata,
    normalize_audit_status,
    sanitize_metadata,
    severity_from_status,
    status_from_http_code,
)


def test_normalize_audit_status_converte_alias():
    assert normalize_audit_status("ok") == "SUCCESS"
    assert normalize_audit_status("error") == "FAILURE"


def test_status_from_http_code():
    assert status_from_http_code(200) == "SUCCESS"
    assert status_from_http_code(404) == "FAILURE"


def test_severity_from_status():
    assert severity_from_status("SUCCESS") == "info"
    assert severity_from_status("FAILURE") == "high"


def test_build_audit_action_padroniza_metodo():
    assert build_audit_action("get", "/membros/") == "GET:/membros/"


def test_sanitize_metadata_remove_sensiveis_recursivo():
    data = {
        "token": "abc",
        "query": "ok",
        "nested": {"password": "x", "campo": 1},
        "items": [{"cpf": "1", "nome": "Ana"}],
    }
    sanitized = sanitize_metadata(data)
    assert "token" not in sanitized
    assert sanitized["nested"] == {"campo": 1}
    assert sanitized["items"] == [{"nome": "Ana"}]


def test_enrich_metadata_inclui_severidade_default():
    enriched = enrich_metadata({"campo": "ok"}, status="FAILURE")
    assert enriched["campo"] == "ok"
    assert enriched["severity"] == "high"

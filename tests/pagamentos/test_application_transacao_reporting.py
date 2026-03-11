import os
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.pagamentos.application.transacao_reporting import (  # noqa: E402
    build_transacoes_csv_content,
    resolve_review_filter,
)


def test_resolve_review_filter_default_and_specific():
    default_filter = resolve_review_filter(raw_status=None)
    specific_filter = resolve_review_filter(raw_status="failed")

    assert default_filter.status_filter == "all"
    assert default_filter.statuses == ["pending", "failed"]
    assert specific_filter.status_filter == "failed"
    assert specific_filter.statuses == ["failed"]


def test_build_transacoes_csv_content():
    transacoes = [
        SimpleNamespace(
            criado_em=datetime(2026, 3, 10, 10, 0, 0),
            valor=Decimal("120.00"),
            status="pending",
            metodo="pix",
        )
    ]

    content = build_transacoes_csv_content(transacoes=transacoes)

    assert content.startswith("data,valor,status,metodo")
    assert "2026-03-10T10:00:00,120.00,pending,pix" in content

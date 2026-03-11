import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.pagamentos.interfaces.reporting_http import (  # noqa: E402
    build_transacao_revisao_context,
    build_transacoes_csv_response,
)


def test_build_transacao_revisao_context():
    transacoes = ["t1", "t2"]
    context = build_transacao_revisao_context(
        transacoes=transacoes,
        status_filtro="failed",
    )
    assert context["transacoes"] == transacoes
    assert context["status_filtro"] == "failed"


def test_build_transacoes_csv_response_sets_headers():
    response = build_transacoes_csv_response(conteudo="data,valor\n2026-03-10,80.00")
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/csv")
    assert response["Content-Disposition"] == "attachment; filename=transacoes.csv"

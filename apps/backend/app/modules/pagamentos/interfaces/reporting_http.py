from __future__ import annotations

from django.http import HttpResponse


def build_transacao_revisao_context(*, transacoes, status_filtro: str) -> dict:
    return {
        "transacoes": transacoes,
        "status_filtro": status_filtro,
    }


def build_transacoes_csv_response(*, conteudo: str) -> HttpResponse:
    response = HttpResponse(conteudo, content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=transacoes.csv"
    return response

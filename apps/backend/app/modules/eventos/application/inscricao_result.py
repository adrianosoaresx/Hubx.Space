from __future__ import annotations

from typing import Any

from django.urls import reverse


def build_inscricao_result_context(
    *,
    request,
    inscricao,
    status: str = "success",
    message: str | None = None,
    title: str = "Status da inscrição",
) -> dict[str, Any]:
    evento = inscricao.evento
    share_url = request.build_absolute_uri(evento.get_absolute_url())
    inscricao_url = reverse("eventos:inscricao_overview", args=[evento.pk])
    convite = evento.convites.first()
    return {
        "evento": evento,
        "inscricao": inscricao,
        "status": status,
        "message": message,
        "share_url": share_url,
        "inscricao_url": inscricao_url,
        "convite": convite,
        "title": title,
    }

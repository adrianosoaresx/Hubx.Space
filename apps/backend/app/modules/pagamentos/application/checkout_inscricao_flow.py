from __future__ import annotations

from eventos.models import InscricaoEvento


def build_checkout_initial_from_inscricao(*, inscricao: InscricaoEvento, user) -> dict[str, object]:
    initial: dict[str, object] = {
        "inscricao_uuid": inscricao.uuid,
        "organizacao_id": inscricao.evento.organizacao_id,
    }
    valor_evento = inscricao.evento.get_valor_para_usuario(user=user)
    if valor_evento is not None:
        initial["valor"] = valor_evento
    return initial

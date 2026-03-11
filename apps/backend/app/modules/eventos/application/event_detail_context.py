from __future__ import annotations

from collections import Counter
from decimal import Decimal
from typing import Any

from accounts.models import UserType


def resolve_event_management_permissions(
    *,
    tipo_usuario: str | None,
    user_has_change_perm: bool,
    user_has_delete_perm: bool,
    coordenador_do_evento: bool,
) -> dict[str, bool]:
    pode_editar_evento = user_has_change_perm
    pode_excluir_evento = user_has_delete_perm

    if tipo_usuario == UserType.COORDENADOR.value and coordenador_do_evento:
        pode_editar_evento = True
        pode_excluir_evento = True

    if tipo_usuario in {UserType.ADMIN.value, UserType.OPERADOR.value}:
        pode_editar_evento = True
        pode_excluir_evento = True

    return {
        "pode_editar_evento": pode_editar_evento,
        "pode_excluir_evento": pode_excluir_evento,
        "pode_gerenciar_inscricoes": tipo_usuario
        in {
            UserType.ADMIN.value,
            UserType.OPERADOR.value,
            UserType.COORDENADOR.value,
        },
        "pode_ver_financeiro": tipo_usuario
        in {
            UserType.ADMIN.value,
            UserType.OPERADOR.value,
        },
        "pode_gerenciar_convites": tipo_usuario
        in {
            UserType.ADMIN.value,
            UserType.OPERADOR.value,
            UserType.COORDENADOR.value,
        },
    }


def sort_inscricoes_financeiro(inscricoes: list[Any]) -> list[Any]:
    inscricoes_financeiro = [inscricao for inscricao in inscricoes if inscricao.status != "cancelada"]
    inscricoes_financeiro.sort(
        key=lambda ins: (
            getattr(ins.user, "contato", None)
            or getattr(ins.user, "display_name", None)
            or ins.user.get_full_name()
            or ins.user.username
            or ""
        ).lower()
    )
    return inscricoes_financeiro


def build_inscricao_status_summary(*, inscricoes: list[Any], participantes_maximo: int | None) -> dict[str, int | None]:
    status_counts = Counter(inscricao.status for inscricao in inscricoes)
    total_confirmadas = status_counts.get("confirmada", 0)
    total_pendentes = status_counts.get("pendente", 0)
    total_canceladas = status_counts.get("cancelada", 0)
    vagas_disponiveis = None
    if participantes_maximo is not None:
        vagas_disponiveis = max(participantes_maximo - total_confirmadas, 0)
    return {
        "total_inscricoes_confirmadas": total_confirmadas,
        "total_inscricoes_pendentes": total_pendentes,
        "total_inscricoes_canceladas": total_canceladas,
        "vagas_disponiveis": vagas_disponiveis,
    }


def build_financeiro_summary(inscricoes_financeiro: list[Any]) -> dict[str, Any]:
    total_pagamentos_validados = sum(1 for inscricao in inscricoes_financeiro if inscricao.pagamento_validado)
    total_pagamentos_pendentes = max(len(inscricoes_financeiro) - total_pagamentos_validados, 0)

    valor_total_pagamentos_validados = Decimal("0.00")
    for inscricao in inscricoes_financeiro:
        if not inscricao.pagamento_validado:
            continue
        valor_referencia = inscricao.valor_pago
        if valor_referencia is None:
            valor_referencia = inscricao.get_valor_evento()
        if valor_referencia is None:
            continue
        valor_total_pagamentos_validados += Decimal(valor_referencia)

    return {
        "total_pagamentos_validados": total_pagamentos_validados,
        "total_pagamentos_pendentes": total_pagamentos_pendentes,
        "valor_total_pagamentos_validados": valor_total_pagamentos_validados,
    }

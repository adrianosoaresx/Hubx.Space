from __future__ import annotations


def can_user_rate_event(*, inscricao_confirmada: bool, evento_data_fim, now) -> bool:
    return bool(inscricao_confirmada) and now > evento_data_fim


def can_cancelar_inscricao(
    *,
    inscricao_confirmada: bool,
    inscricao_permitida: bool,
    evento_data_inicio,
    pagamento_validado: bool,
    now,
) -> bool:
    return (
        bool(inscricao_confirmada)
        and inscricao_permitida
        and now < evento_data_inicio
        and not pagamento_validado
    )


def parse_feedback_nota(raw_nota) -> tuple[int | None, str | None]:
    try:
        nota = int(raw_nota)
    except (TypeError, ValueError):
        return None, "Nota inválida."
    if nota not in range(1, 6):
        return None, "Nota fora do intervalo permitido (1–5)."
    return nota, None

from __future__ import annotations

from dataclasses import dataclass

from pagamentos.models import Transacao


@dataclass(frozen=True)
class TransacaoReviewResult:
    status_filter: str
    statuses: list[str]


def resolve_review_filter(*, raw_status: str | None) -> TransacaoReviewResult:
    status_filter = (raw_status or "all").strip().lower() or "all"
    statuses = [Transacao.Status.PENDENTE, Transacao.Status.FALHOU]
    if status_filter in Transacao.Status.values:
        statuses = [status_filter]
    return TransacaoReviewResult(status_filter=status_filter, statuses=statuses)


def build_transacoes_csv_content(*, transacoes) -> str:
    lines = ["data,valor,status,metodo"]
    for transacao in transacoes:
        lines.append(
            f"{transacao.criado_em.isoformat()},{transacao.valor},{transacao.status},{transacao.metodo}"
        )
    return "\n".join(lines)

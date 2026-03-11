from __future__ import annotations


def resolve_participante_nome(inscricao) -> str:
    user = getattr(inscricao, "user", None)
    if not user:
        return "-"
    for candidate in (
        getattr(user, "contato", None),
        getattr(user, "display_name", None),
        getattr(user, "get_full_name", None),
        getattr(user, "username", None),
    ):
        if callable(candidate):
            candidate = candidate()
        if candidate:
            return str(candidate).strip()
    return "-"


def inscricao_sort_key(inscricao) -> tuple[str, int]:
    nome = resolve_participante_nome(inscricao).casefold()
    return nome, getattr(inscricao, "pk", 0) or 0


def prepare_inscricoes_for_report(inscricoes_queryset):
    inscricoes = sorted(inscricoes_queryset, key=inscricao_sort_key)
    for inscricao in inscricoes:
        inscricao.participante_nome = resolve_participante_nome(inscricao)
    return inscricoes

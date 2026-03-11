from __future__ import annotations

from accounts.models import UserType
from apps.backend.app.modules.membros.application.membership_policies import (
    resolve_membership_target_user_type,
    should_clear_primary_nucleo,
)
from nucleos.models import Nucleo, ParticipacaoNucleo


def sync_promocao_member_state(
    *,
    membro,
    organizacao,
    is_guest: bool,
    promote_associado: bool,
) -> list[str]:
    remaining_participacoes = ParticipacaoNucleo.objects.filter(
        user=membro,
        status="ativo",
        status_suspensao=False,
    )
    has_coordenador = remaining_participacoes.filter(papel="coordenador").exists()
    has_participacao = remaining_participacoes.exists()
    has_consultor = Nucleo.objects.filter(
        organizacao=organizacao,
        consultor=membro,
    ).exists()

    updates: list[str] = []
    if is_guest and promote_associado:
        if membro.user_type != UserType.ASSOCIADO.value:
            membro.user_type = UserType.ASSOCIADO.value
            updates.append("user_type")
        if not membro.is_associado:
            membro.is_associado = True
            updates.append("is_associado")

    if membro.is_coordenador != has_coordenador:
        membro.is_coordenador = has_coordenador
        updates.append("is_coordenador")

    if should_clear_primary_nucleo(
        has_participacao=has_participacao,
        has_coordenador=has_coordenador,
        has_consultor=has_consultor,
    ):
        if membro.nucleo is not None:
            membro.nucleo = None
            updates.append("nucleo")

    target_type = resolve_membership_target_user_type(
        current_type=membro.user_type,
        has_coordenador=has_coordenador,
        has_consultor=has_consultor,
        has_participacao=has_participacao,
    )
    if target_type and membro.user_type != target_type:
        membro.user_type = target_type
        updates.append("user_type")

    if updates:
        membro.save(update_fields=updates)

    return updates

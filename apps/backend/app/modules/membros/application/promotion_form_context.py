from __future__ import annotations

import json
from collections import defaultdict

from django.db.models import Prefetch
from django.utils.translation import gettext_lazy as _

from accounts.models import UserType
from nucleos.models import Nucleo, ParticipacaoNucleo


def build_promocao_form_context(
    *,
    membro,
    organizacao,
    selected_nucleado: list[str] | None = None,
    selected_consultor: list[str] | None = None,
    selected_coordenador: list[str] | None = None,
    selected_coordenador_roles: dict[str, str] | None = None,
    selected_remover_nucleado: list[str] | None = None,
    selected_remover_consultor: list[str] | None = None,
    selected_remover_coordenador: list[str] | None = None,
    form_errors: list[str] | None = None,
    success_message: str | None = None,
    origin_section: str = "",
) -> dict[str, object]:
    selected_nucleado_values = [str(value) for value in selected_nucleado or []]
    selected_consultor_values = [str(value) for value in selected_consultor or []]
    selected_coordenador_values = [str(value) for value in selected_coordenador or []]
    selected_remover_nucleado_values = [str(value) for value in selected_remover_nucleado or []]
    selected_remover_consultor_values = [str(value) for value in selected_remover_consultor or []]
    selected_remover_coordenador_values = [
        str(value) for value in selected_remover_coordenador or []
    ]
    selected_role_values = {
        str(key): value for key, value in (selected_coordenador_roles or {}).items()
    }
    form_error_values = form_errors or []

    nucleos_qs = (
        Nucleo.objects.filter(organizacao=organizacao)
        .select_related("consultor")
        .prefetch_related(
            Prefetch(
                "participacoes",
                queryset=ParticipacaoNucleo.objects.filter(
                    status="ativo", papel="coordenador"
                ).select_related("user"),
            )
        )
        .order_by("nome")
    )

    role_labels = dict(ParticipacaoNucleo.PapelCoordenador.choices)
    participacoes_usuario = list(
        ParticipacaoNucleo.objects.filter(
            user=membro,
            status="ativo",
            status_suspensao=False,
        ).values("nucleo_id", "papel", "papel_coordenador")
    )

    current_memberships: set[str] = set()
    user_roles_by_nucleo: defaultdict[str, list[str]] = defaultdict(list)
    user_role_map: defaultdict[str, list[str]] = defaultdict(list)
    for participacao in participacoes_usuario:
        nucleo_id = str(participacao["nucleo_id"])
        current_memberships.add(nucleo_id)
        if participacao["papel"] == "coordenador" and participacao["papel_coordenador"]:
            papel = participacao["papel_coordenador"]
            user_roles_by_nucleo[nucleo_id].append(papel)
            user_role_map[papel].append(nucleo_id)

    nucleos: list[dict[str, object]] = []
    for nucleo in nucleos_qs:
        participacoes = list(nucleo.participacoes.all())
        unavailable_roles: set[str] = set()
        coordenadores: list[dict[str, object]] = []
        unavailable_messages: dict[str, str] = {}

        for participacao in participacoes:
            papel = participacao.papel_coordenador
            if not papel:
                continue
            unavailable_roles.add(papel)
            is_target = participacao.user_id == membro.pk
            coordenadores.append(
                {
                    "papel": papel,
                    "user_name": participacao.user.display_name
                    or participacao.user.username,
                    "user_id": participacao.user_id,
                    "is_target_user": is_target,
                }
            )
            if not is_target:
                unavailable_messages[papel] = _("%(papel)s ocupado por %(nome)s.") % {
                    "papel": role_labels.get(papel, papel),
                    "nome": participacao.user.display_name or participacao.user.username,
                }

        coordenadores.sort(key=lambda item: role_labels.get(item["papel"], item["papel"]))

        nucleos.append(
            {
                "id": str(nucleo.pk),
                "nome": nucleo.nome,
                "avatar_url": nucleo.avatar.url if nucleo.avatar else "",
                "consultor_name": (
                    nucleo.consultor.display_name or nucleo.consultor.username
                    if nucleo.consultor
                    else ""
                ),
                "is_current_consultor": nucleo.consultor_id == membro.pk,
                "is_current_member": str(nucleo.pk) in current_memberships,
                "is_current_coordinator": bool(user_roles_by_nucleo.get(str(nucleo.pk), [])),
                "coordenadores": coordenadores,
                "unavailable_roles": sorted(unavailable_roles),
                "user_current_roles": user_roles_by_nucleo.get(str(nucleo.pk), []),
                "unavailable_messages_json": json.dumps(unavailable_messages),
            }
        )

    restricted_roles = [
        ParticipacaoNucleo.PapelCoordenador.COORDENADOR_GERAL,
        ParticipacaoNucleo.PapelCoordenador.VICE_COORDENADOR,
    ]

    return {
        "membro": membro,
        "is_guest": membro.user_type == UserType.CONVIDADO.value,
        "nucleos": nucleos,
        "coordenador_role_choices": ParticipacaoNucleo.PapelCoordenador.choices,
        "coordenador_role_labels": role_labels,
        "restricted_roles": [role for role in restricted_roles if role],
        "selected_nucleado": selected_nucleado_values,
        "selected_consultor": selected_consultor_values,
        "selected_coordenador": selected_coordenador_values,
        "selected_coordenador_roles": selected_role_values,
        "selected_remover_nucleado": selected_remover_nucleado_values,
        "selected_remover_consultor": selected_remover_consultor_values,
        "selected_remover_coordenador": selected_remover_coordenador_values,
        "form_errors": form_error_values,
        "success_message": success_message,
        "user_role_map_json": json.dumps(dict(user_role_map)),
        "origin_section": origin_section,
    }

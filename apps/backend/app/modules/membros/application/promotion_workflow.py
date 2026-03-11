from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from django.utils.translation import gettext_lazy as _

from accounts.models import UserType
from apps.backend.app.modules.membros.application.membership_policies import (
    parse_promote_associado_flag,
)
from apps.backend.app.modules.membros.application.promotion_conflicts import (
    validate_promocao_conflicts,
)
from apps.backend.app.modules.membros.application.promotion_member_state import (
    sync_promocao_member_state,
)
from apps.backend.app.modules.membros.application.promotion_persistence import (
    apply_promocao_persistence,
)
from apps.backend.app.modules.membros.application.promotion_selection import (
    PromotionSelection,
    build_promocao_selection,
    extract_coordenador_role_values,
)
from nucleos.models import Nucleo


@dataclass(frozen=True)
class PromocaoWorkflowResult:
    success: bool
    form_errors: list[str]
    selected_nucleado: list[str]
    selected_consultor: list[str]
    selected_coordenador: list[str]
    selected_coordenador_roles: dict[str, str]
    selected_remover_nucleado: list[str]
    selected_remover_consultor: list[str]
    selected_remover_coordenador: list[str]


@dataclass(frozen=True)
class PromocaoWorkflowInput:
    selection: PromotionSelection
    promote_associado: bool
    is_guest: bool


class PostDataLike(Protocol):
    def get(self, key: str, default: Any = None) -> Any:
        ...

    def getlist(self, key: str) -> list[str]:
        ...


def build_promocao_input(
    *,
    current_user_type: str | None,
    raw_nucleado: list[str],
    raw_consultor: list[str],
    raw_coordenador: list[str],
    raw_remover_nucleado: list[str],
    raw_remover_consultor: list[str],
    raw_remover_coordenador: list[str],
    role_values_by_nucleo: Mapping[str, str],
    raw_promover_associado: str | None,
) -> PromocaoWorkflowInput:
    selection = build_promocao_selection(
        raw_nucleado=raw_nucleado,
        raw_consultor=raw_consultor,
        raw_coordenador=raw_coordenador,
        raw_remover_nucleado=raw_remover_nucleado,
        raw_remover_consultor=raw_remover_consultor,
        raw_remover_coordenador=raw_remover_coordenador,
        role_values_by_nucleo=role_values_by_nucleo,
    )
    return PromocaoWorkflowInput(
        selection=selection,
        promote_associado=parse_promote_associado_flag(raw_promover_associado),
        is_guest=current_user_type == UserType.CONVIDADO.value,
    )


def execute_promocao_from_post(
    *,
    membro,
    organizacao,
    post_data: PostDataLike,
) -> PromocaoWorkflowResult:
    workflow_input = build_promocao_input(
        current_user_type=membro.user_type,
        raw_nucleado=post_data.getlist("nucleado_nucleos"),
        raw_consultor=post_data.getlist("consultor_nucleos"),
        raw_coordenador=post_data.getlist("coordenador_nucleos"),
        raw_remover_nucleado=post_data.getlist("remover_nucleado_nucleos"),
        raw_remover_consultor=post_data.getlist("remover_consultor_nucleos"),
        raw_remover_coordenador=post_data.getlist("remover_coordenador_nucleos"),
        role_values_by_nucleo=extract_coordenador_role_values(post_data),
        raw_promover_associado=post_data.get("promover_associado"),
    )

    return execute_promocao_workflow(
        membro=membro,
        organizacao=organizacao,
        workflow_input=workflow_input,
    )


def execute_promocao_workflow(
    *,
    membro,
    organizacao,
    workflow_input: PromocaoWorkflowInput,
) -> PromocaoWorkflowResult:
    selection = workflow_input.selection
    form_errors: list[str] = []
    if not selection.all_action_ids and not (
        workflow_input.is_guest and workflow_input.promote_associado
    ):
        form_errors.append(_("Selecione ao menos um núcleo e papel para promoção ou remoção."))

    valid_action_ids: set[int] = set()
    if selection.all_action_ids:
        valid_action_ids = set(
            Nucleo.objects.filter(
                organizacao=organizacao, id__in=selection.all_action_ids
            ).values_list("id", flat=True)
        )
        if len(valid_action_ids) != len(selection.all_action_ids):
            form_errors.append(_("Selecione núcleos válidos da organização."))

    valid_ids = set(nid for nid in selection.all_selected_ids if nid in valid_action_ids)

    conflict_errors, valid_consultor_ids = validate_promocao_conflicts(
        membro=membro,
        coordenador_ids=selection.coordenador_ids,
        coordenador_roles=selection.coordenador_roles,
        valid_action_ids=valid_action_ids,
        nucleado_ids=selection.nucleado_ids,
        consultor_ids=selection.consultor_ids,
        remover_nucleado_ids=selection.remover_nucleado_ids,
        remover_consultor_ids=selection.remover_consultor_ids,
        remover_coordenador_ids=selection.remover_coordenador_ids,
    )
    form_errors.extend(conflict_errors)

    if form_errors:
        return PromocaoWorkflowResult(
            success=False,
            form_errors=form_errors,
            selected_nucleado=[str(pk) for pk in selection.nucleado_ids],
            selected_consultor=[str(pk) for pk in selection.consultor_ids],
            selected_coordenador=[str(pk) for pk in selection.coordenador_ids],
            selected_coordenador_roles=selection.selected_coordenador_roles,
            selected_remover_nucleado=[str(pk) for pk in selection.remover_nucleado_ids],
            selected_remover_consultor=[str(pk) for pk in selection.remover_consultor_ids],
            selected_remover_coordenador=[str(pk) for pk in selection.remover_coordenador_ids],
        )

    if not valid_action_ids and not (
        workflow_input.is_guest and workflow_input.promote_associado
    ):
        return PromocaoWorkflowResult(
            success=False,
            form_errors=[_("Nenhum núcleo válido foi selecionado.")],
            selected_nucleado=[],
            selected_consultor=[],
            selected_coordenador=[],
            selected_coordenador_roles={},
            selected_remover_nucleado=[],
            selected_remover_consultor=[],
            selected_remover_coordenador=[],
        )

    apply_promocao_persistence(
        membro=membro,
        organizacao=organizacao,
        valid_action_ids=valid_action_ids,
        valid_ids=valid_ids,
        valid_consultor_ids=valid_consultor_ids,
        nucleado_ids=selection.nucleado_ids,
        coordenador_roles=selection.coordenador_roles,
        remover_nucleado_ids=selection.remover_nucleado_ids,
        remover_consultor_ids=selection.remover_consultor_ids,
        remover_coordenador_ids=selection.remover_coordenador_ids,
    )

    sync_promocao_member_state(
        membro=membro,
        organizacao=organizacao,
        is_guest=workflow_input.is_guest,
        promote_associado=workflow_input.promote_associado,
    )

    return PromocaoWorkflowResult(
        success=True,
        form_errors=[],
        selected_nucleado=[],
        selected_consultor=[],
        selected_coordenador=[],
        selected_coordenador_roles={},
        selected_remover_nucleado=[],
        selected_remover_consultor=[],
        selected_remover_coordenador=[],
    )

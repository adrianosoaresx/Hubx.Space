from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class PromotionSelection:
    nucleado_ids: list[int]
    consultor_ids: list[int]
    coordenador_ids: list[int]
    remover_nucleado_ids: list[int]
    remover_consultor_ids: list[int]
    remover_coordenador_ids: list[int]
    selected_coordenador_roles: dict[str, str]
    coordenador_roles: dict[int, str]
    all_selected_ids: set[int]
    removal_ids: set[int]
    all_action_ids: set[int]


def parse_unique_int_ids(values: list[str]) -> list[int]:
    parsed: list[int] = []
    seen: set[int] = set()
    for value in values:
        try:
            pk = int(value)
        except (TypeError, ValueError):
            continue
        if pk not in seen:
            parsed.append(pk)
            seen.add(pk)
    return parsed


def extract_coordenador_role_values(post_data: Mapping[str, str]) -> dict[str, str]:
    role_values: dict[str, str] = {}
    for key, value in post_data.items():
        if not key.startswith("coordenador_papel_"):
            continue
        nucleo_id = key.replace("coordenador_papel_", "", 1).strip()
        if nucleo_id:
            role_values[nucleo_id] = (value or "").strip()
    return role_values


def build_promocao_selection(
    *,
    raw_nucleado: list[str],
    raw_consultor: list[str],
    raw_coordenador: list[str],
    raw_remover_nucleado: list[str],
    raw_remover_consultor: list[str],
    raw_remover_coordenador: list[str],
    role_values_by_nucleo: Mapping[str, str],
) -> PromotionSelection:
    nucleado_ids = parse_unique_int_ids(raw_nucleado)
    consultor_ids = parse_unique_int_ids(raw_consultor)
    coordenador_ids = parse_unique_int_ids(raw_coordenador)
    remover_nucleado_ids = parse_unique_int_ids(raw_remover_nucleado)
    remover_consultor_ids = parse_unique_int_ids(raw_remover_consultor)
    remover_coordenador_ids = parse_unique_int_ids(raw_remover_coordenador)

    selected_coordenador_roles: dict[str, str] = {}
    coordenador_roles: dict[int, str] = {}
    for nucleo_id in coordenador_ids:
        role_value = (role_values_by_nucleo.get(str(nucleo_id)) or "").strip()
        selected_coordenador_roles[str(nucleo_id)] = role_value
        if role_value:
            coordenador_roles[nucleo_id] = role_value

    all_selected_ids = set(nucleado_ids) | set(consultor_ids) | set(coordenador_ids)
    removal_ids = (
        set(remover_nucleado_ids)
        | set(remover_consultor_ids)
        | set(remover_coordenador_ids)
    )
    all_action_ids = all_selected_ids | removal_ids

    return PromotionSelection(
        nucleado_ids=nucleado_ids,
        consultor_ids=consultor_ids,
        coordenador_ids=coordenador_ids,
        remover_nucleado_ids=remover_nucleado_ids,
        remover_consultor_ids=remover_consultor_ids,
        remover_coordenador_ids=remover_coordenador_ids,
        selected_coordenador_roles=selected_coordenador_roles,
        coordenador_roles=coordenador_roles,
        all_selected_ids=all_selected_ids,
        removal_ids=removal_ids,
        all_action_ids=all_action_ids,
    )

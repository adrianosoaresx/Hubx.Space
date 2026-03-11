from __future__ import annotations

from accounts.models import UserType


PROMOCAO_ALLOWED_ROLES = {UserType.ADMIN.value, UserType.OPERADOR.value}


def resolve_allowed_user_types_for_creator(tipo_usuario: str | None) -> list[str]:
    if tipo_usuario in {UserType.ADMIN.value, UserType.ROOT.value}:
        return [UserType.ASSOCIADO.value, UserType.OPERADOR.value]
    if tipo_usuario == UserType.OPERADOR.value:
        return [UserType.ASSOCIADO.value]
    return []


def can_access_promocao(tipo_usuario: str | None) -> bool:
    return tipo_usuario in PROMOCAO_ALLOWED_ROLES


def parse_promote_associado_flag(raw_value: str | None) -> bool:
    return (raw_value or "").strip().lower() in {"1", "true", "on", "yes"}


def resolve_membership_target_user_type(
    *,
    current_type: str | None,
    has_coordenador: bool,
    has_consultor: bool,
    has_participacao: bool,
) -> str | None:
    allowed_types = {
        UserType.ASSOCIADO.value,
        UserType.NUCLEADO.value,
        UserType.CONSULTOR.value,
        UserType.COORDENADOR.value,
    }
    if current_type not in allowed_types:
        return None
    if has_coordenador:
        return UserType.COORDENADOR.value
    if has_consultor:
        return UserType.CONSULTOR.value
    if has_participacao:
        return UserType.NUCLEADO.value
    return UserType.ASSOCIADO.value


def should_clear_primary_nucleo(
    *, has_participacao: bool, has_coordenador: bool, has_consultor: bool
) -> bool:
    return not (has_participacao or has_coordenador or has_consultor)

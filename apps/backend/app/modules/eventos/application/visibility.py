from __future__ import annotations

from accounts.models import UserType


def get_tipo_usuario(user) -> str | None:
    tipo = getattr(user, "get_tipo_usuario", None)
    if isinstance(tipo, UserType):
        return tipo.value
    if hasattr(tipo, "value"):
        return tipo.value
    return tipo


def is_guest_user(user) -> bool:
    return get_tipo_usuario(user) == UserType.CONVIDADO.value


def get_nucleos_coordenacao_consultoria_ids(user) -> set[int]:
    nucleo_ids: set[int] = set()

    nucleo_id = getattr(user, "nucleo_id", None)
    if nucleo_id:
        nucleo_ids.add(nucleo_id)

    participacoes = getattr(user, "participacoes", None)
    if participacoes is not None:
        coordenacoes = participacoes.filter(
            papel="coordenador",
            status="ativo",
            status_suspensao=False,
        ).values_list("nucleo_id", flat=True)
        nucleo_ids.update(pk for pk in coordenacoes if pk)

    nucleos_consultoria = getattr(user, "nucleos_consultoria", None)
    if nucleos_consultoria is not None:
        consultoria_ids = nucleos_consultoria.values_list("id", flat=True)
        nucleo_ids.update(pk for pk in consultoria_ids if pk)

    return nucleo_ids


def resolve_planejamento_permissions(user):
    if is_guest_user(user):
        return False, None

    tipo_usuario = get_tipo_usuario(user)
    can_view = tipo_usuario not in {
        UserType.ASSOCIADO.value,
        UserType.NUCLEADO.value,
    }
    nucleo_ids_limit: set[int] | None = None
    if can_view and tipo_usuario in {UserType.COORDENADOR.value, UserType.CONSULTOR.value}:
        nucleo_ids_limit = get_nucleos_coordenacao_consultoria_ids(user)
    return can_view, nucleo_ids_limit


def is_user_event_coordinator(user, evento) -> bool:
    evento_nucleo_id = getattr(evento, "nucleo_id", None)
    if evento_nucleo_id is None:
        return False

    participacoes = getattr(user, "participacoes", None)
    if participacoes is not None:
        if participacoes.filter(
            nucleo=getattr(evento, "nucleo", None),
            papel="coordenador",
            status="ativo",
            status_suspensao=False,
        ).exists():
            return True

    return getattr(user, "nucleo_id", None) == evento_nucleo_id and getattr(
        user, "is_coordenador", False
    )


def has_restricted_event_access(user, evento) -> bool:
    tipo_usuario = get_tipo_usuario(user)
    if tipo_usuario in {UserType.ADMIN.value, UserType.OPERADOR.value}:
        return True
    if tipo_usuario != UserType.COORDENADOR.value:
        return False
    return is_user_event_coordinator(user, evento)


def can_manage_event_portfolio(user, evento) -> bool:
    tipo_usuario = get_tipo_usuario(user)
    if tipo_usuario in {UserType.ADMIN.value, UserType.OPERADOR.value}:
        return True
    if user.has_perm("eventos.change_evento"):
        return True
    if tipo_usuario == UserType.COORDENADOR.value and is_user_event_coordinator(user, evento):
        return True
    return False


def can_view_event_subscribers(user, evento) -> bool:
    return has_restricted_event_access(user, evento)

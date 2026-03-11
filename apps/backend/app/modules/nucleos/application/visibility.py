from __future__ import annotations

from accounts.models import UserType
from nucleos.models import Nucleo


def user_has_consultoria_access(user) -> bool:
    tipo = getattr(user, "get_tipo_usuario", None)
    if tipo == UserType.CONSULTOR.value:
        return True

    user_type = getattr(user, "user_type", None)
    if user_type in {UserType.CONSULTOR, UserType.CONSULTOR.value}:
        return True

    nucleos_consultoria = getattr(user, "nucleos_consultoria", None)
    if nucleos_consultoria is not None:
        try:
            return nucleos_consultoria.filter(deleted=False).exists()
        except Exception:
            return False
    return False


def get_consultor_nucleo_ids(user) -> set[int]:
    nucleo_ids: set[int] = set()

    nucleos_consultoria = getattr(user, "nucleos_consultoria", None)
    if nucleos_consultoria is not None:
        try:
            nucleo_ids.update(pk for pk in nucleos_consultoria.values_list("id", flat=True) if pk)
        except Exception:
            pass

    participacoes = getattr(user, "participacoes", None)
    if participacoes is not None:
        participacao_ids = participacoes.filter(
            status="ativo",
            status_suspensao=False,
        ).values_list("nucleo_id", flat=True)
        nucleo_ids.update(pk for pk in participacao_ids if pk)

    nucleo_id = getattr(user, "nucleo_id", None)
    if nucleo_id:
        nucleo_ids.add(nucleo_id)

    return nucleo_ids


def get_allowed_classificacao_keys(user) -> set[str]:
    all_keys = {choice.value for choice in Nucleo.Classificacao}
    tipo = getattr(user, "get_tipo_usuario", None)

    if tipo in {
        UserType.ADMIN.value,
        UserType.OPERADOR.value,
        UserType.ROOT.value,
    }:
        return all_keys

    if user_has_consultoria_access(user):
        return all_keys

    return {Nucleo.Classificacao.CONSTITUIDO.value}


def user_can_manage_nucleacao_requests(
    user,
    nucleo,
    consultor_ids: set[int] | None = None,
) -> bool:
    consultor_ids = consultor_ids or set()
    tipo = getattr(user, "get_tipo_usuario", None)
    if isinstance(tipo, UserType):
        tipo = tipo.value

    if tipo == UserType.ADMIN.value:
        return getattr(user, "organizacao_id", None) == getattr(nucleo, "organizacao_id", None)

    if tipo == UserType.COORDENADOR.value:
        participacoes = getattr(nucleo, "participacoes", None)
        if participacoes is not None:
            return participacoes.filter(
                user=user,
                status="ativo",
                status_suspensao=False,
            ).exists()
        return False

    if tipo == UserType.CONSULTOR.value or consultor_ids:
        return nucleo.pk in consultor_ids

    return False


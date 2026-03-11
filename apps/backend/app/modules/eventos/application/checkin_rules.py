from __future__ import annotations

from accounts.models import UserType


def checkin_requires_post(request_method: str) -> bool:
    return request_method == "POST"


def user_can_access_checkin_form(*, evento, user, inscricao, tipo_usuario: str | None) -> bool:
    if evento.organizacao != getattr(user, "organizacao", None):
        return False

    staff_tipos = {UserType.ADMIN.value, UserType.COORDENADOR.value}
    if hasattr(UserType, "GERENTE"):
        staff_tipos.add(UserType.GERENTE.value)

    if user == inscricao.user:
        return True
    return tipo_usuario in staff_tipos


def user_can_execute_checkin(*, evento, user) -> bool:
    return evento.organizacao == getattr(user, "organizacao", None)


def validate_checkin_codigo(
    *,
    codigo: str,
    inscricao_pk: int,
    checksum_generator,
) -> tuple[bool, str | None]:
    codigo_limpo = (codigo or "").strip()
    if not codigo_limpo or "inscricao:" not in codigo_limpo:
        return False, "Código inválido."

    partes_codigo = codigo_limpo.split(":", 2)
    if len(partes_codigo) < 2 or not partes_codigo[1]:
        return False, "Código inválido."

    codigo_inscricao = partes_codigo[1]
    checksum = partes_codigo[2] if len(partes_codigo) > 2 else None

    if str(inscricao_pk) != codigo_inscricao:
        return False, "Código inválido."

    if checksum and not checksum.startswith("{"):
        expected = checksum_generator(str(inscricao_pk))
        if checksum != expected:
            return False, "Código inválido."

    return True, None


def is_inscricao_confirmada(status: str | None) -> bool:
    return status == "confirmada"


def build_checkin_form_context(*, evento, inscricao, title, subtitle):
    return {
        "evento": evento,
        "inscricao": inscricao,
        "title": title,
        "subtitle": subtitle,
    }


def build_checkin_success_payload(*, already_done: bool) -> dict[str, str]:
    if already_done:
        return {"status": "ok", "message": "Check-in já realizado."}
    return {"status": "ok"}

from __future__ import annotations

from decimal import Decimal
from typing import Any


def can_user_access_checkout(
    *,
    request_user: Any,
    inscricao_user: Any,
    has_restricted_access: bool,
) -> bool:
    return request_user == inscricao_user or has_restricted_access


def should_redirect_after_checkout_approval(*, transacao: Any | None, approved_status: str) -> bool:
    return bool(transacao and getattr(transacao, "status", None) == approved_status)


def build_checkout_profile_data(usuario: Any | None) -> dict[str, str]:
    checkout_profile_data = {"nome": "", "email": "", "documento": ""}
    if not usuario:
        return checkout_profile_data

    nome = ""
    if hasattr(usuario, "get_full_name"):
        nome = usuario.get_full_name() or ""
    checkout_profile_data["nome"] = nome or getattr(usuario, "name", "") or getattr(
        usuario, "username", ""
    )
    if getattr(usuario, "email", None):
        checkout_profile_data["email"] = usuario.email
    checkout_profile_data["documento"] = getattr(usuario, "cpf", "") or getattr(
        usuario, "cnpj", ""
    )
    return checkout_profile_data


def build_initial_checkout_data(
    *,
    valor_evento: Any | None,
    checkout_profile_data: dict[str, str],
    default_metodo: str,
    inscricao_uuid: Any | None = None,
) -> dict[str, Any]:
    initial_checkout: dict[str, Any] = {}
    if valor_evento is not None:
        initial_checkout["valor"] = valor_evento
    if inscricao_uuid is not None:
        initial_checkout["inscricao_uuid"] = inscricao_uuid

    if checkout_profile_data.get("nome"):
        initial_checkout["nome"] = checkout_profile_data["nome"]
    if checkout_profile_data.get("email"):
        initial_checkout["email"] = checkout_profile_data["email"]
    if checkout_profile_data.get("documento"):
        initial_checkout["documento"] = checkout_profile_data["documento"]
    if not initial_checkout.get("metodo"):
        initial_checkout["metodo"] = default_metodo
    return initial_checkout


def is_evento_gratuito(evento: Any, user: Any) -> bool:
    valor_evento = evento.get_valor_para_usuario(user=user)
    return bool(getattr(evento, "gratuito", False)) or (
        valor_evento is not None and Decimal(valor_evento) == 0
    )


def is_checkout_required(
    *,
    evento: Any,
    user: Any,
    provider_public_key: str | None,
    metodo_pagamento: str | None = None,
    inscricao_metodo_pagamento: str | None = None,
    pix_metodo: str = "pix",
) -> bool:
    if metodo_pagamento and metodo_pagamento != pix_metodo:
        return False
    if inscricao_metodo_pagamento and inscricao_metodo_pagamento != pix_metodo:
        return False
    if not provider_public_key:
        return False
    if is_evento_gratuito(evento, user):
        return False
    valor_evento = evento.get_valor_para_usuario(user=user)
    if valor_evento is None:
        return False
    return Decimal(valor_evento) > 0


def resolve_metodo_pagamento(transacao: Any | None, metodo_pagamento: str | None) -> str | None:
    if metodo_pagamento:
        return metodo_pagamento
    if transacao is None:
        return None
    return getattr(transacao, "metodo", None)


def should_block_checkout_without_confirmation(
    *,
    checkout_required: bool,
    transacao: Any | None,
    metodo_pagamento: str | None,
) -> bool:
    return checkout_required and transacao is None and not metodo_pagamento


def build_checkout_inscricao_updates(
    *,
    valor_evento: Any | None,
    transacao: Any | None,
    metodo_pagamento: str | None,
    approved_status: str,
) -> dict[str, Any]:
    updates: dict[str, Any] = {}
    if valor_evento is not None:
        updates["valor_pago"] = valor_evento

    if transacao is not None:
        updates["transacao"] = transacao
        updates["metodo_pagamento"] = getattr(transacao, "metodo", None)
        updates["pagamento_validado"] = getattr(transacao, "status", None) == approved_status
        return updates

    if metodo_pagamento:
        updates["metodo_pagamento"] = metodo_pagamento
    return updates


def should_confirm_checkout_inscricao(*, transacao: Any | None, approved_status: str) -> bool:
    return bool(transacao and getattr(transacao, "status", None) == approved_status)

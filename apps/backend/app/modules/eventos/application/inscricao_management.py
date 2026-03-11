from __future__ import annotations

from typing import Any

from django.utils.translation import gettext_lazy as _

from accounts.models import UserType


def build_inscricao_update_queryset(base_queryset, eventos_queryset):
    return base_queryset.select_related("evento", "user").filter(evento__in=eventos_queryset)


def build_inscricao_form_kwargs(inscricao) -> dict[str, Any]:
    return {
        "evento": getattr(inscricao, "evento", None),
        "user": getattr(inscricao, "user", None),
    }


def build_inscricao_update_context(
    *,
    evento,
    back_href: str,
    valor_evento_usuario,
) -> dict[str, Any]:
    return {
        "evento": evento,
        "title": _("Editar inscrição"),
        "subtitle": getattr(evento, "descricao", None),
        "back_href": back_href,
        "valor_evento_usuario": valor_evento_usuario,
        "show_comprovante_pagamento": True,
    }


def resolve_inscricao_valor_pago(*, valor_evento_usuario, valor_pago_atual):
    if valor_evento_usuario is None:
        return valor_pago_atual
    return valor_evento_usuario


def can_toggle_pagamento_validacao(*, tipo_usuario: str | None, user_organizacao_id, evento_organizacao_id) -> bool:
    return (
        tipo_usuario in {UserType.ADMIN.value, UserType.OPERADOR.value}
        and user_organizacao_id == evento_organizacao_id
    )


def toggle_pagamento_validado_status(*, pagamento_validado_atual: bool) -> bool:
    return not pagamento_validado_atual

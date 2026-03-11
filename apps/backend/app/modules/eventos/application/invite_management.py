from __future__ import annotations

from typing import Any

from django.utils.translation import gettext_lazy as _

from accounts.models import UserType


def can_user_manage_convites(tipo_usuario: str | None) -> bool:
    return tipo_usuario in {
        UserType.ADMIN.value,
        UserType.OPERADOR.value,
        UserType.COORDENADOR.value,
    }


def build_convite_create_context(
    *,
    evento: Any,
    form: Any,
    back_href: str,
    fallback_url: str,
) -> dict[str, Any]:
    return {
        "evento": evento,
        "form": form,
        "back_href": back_href,
        "cancel_component_config": {"href": fallback_url, "fallback_href": fallback_url},
        "title": _("Novo convite"),
        "subtitle": evento.titulo,
    }

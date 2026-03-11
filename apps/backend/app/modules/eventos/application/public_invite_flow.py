from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from django.utils.translation import gettext_lazy as _


def build_login_redirect_url(*, login_url: str, inscricao_url: str) -> str:
    return f"{login_url}?{urlencode({'next': inscricao_url})}"


def build_register_url(*, token_url: str, evento_pk: Any, codigo: str) -> str:
    return f"{token_url}?{urlencode({'evento': evento_pk, 'token': codigo})}"


def build_public_invite_email_context(*, evento: Any, codigo: str, token_link: str) -> dict[str, Any]:
    return {
        "evento": evento,
        "codigo": codigo,
        "token_link": token_link,
    }


def build_public_invite_email_subject(*, evento_titulo: str) -> str:
    return str(_("Confirme sua inscrição em %(evento)s") % {"evento": evento_titulo})


def build_public_invite_info_context(
    *,
    convite: Any,
    evento: Any,
    email: str,
    share_url: str,
    register_url: str,
) -> dict[str, Any]:
    return {
        "convite": convite,
        "evento": evento,
        "email": email,
        "share_url": share_url,
        "register_url": register_url,
    }


def build_public_invite_page_context(
    *,
    convite: Any,
    evento: Any,
    inscricao_url: str,
    share_url: str,
    form: Any,
) -> dict[str, Any]:
    return {
        "convite": convite,
        "evento": evento,
        "inscricao_url": inscricao_url,
        "share_url": share_url,
        "form": form,
    }

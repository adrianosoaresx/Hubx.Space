from __future__ import annotations

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from accounts.models import UserType
from tokens.models import TokenAcesso

ROOT_TOKENS_FORBIDDEN_MESSAGE = _("Usuários root não gerenciam tokens de acesso.")


def redirect_root_from_tokens(request):
    user_type = getattr(request.user, "get_tipo_usuario", None)
    if user_type == UserType.ROOT.value:
        messages.error(request, ROOT_TOKENS_FORBIDDEN_MESSAGE)
        return redirect("organizacoes:list")
    return None


def get_query_param(request, key: str):
    """Recupera query string incluindo variação com ``amp;``."""
    return request.GET.get(key) or request.GET.get(f"amp;{key}")


def build_invite_totals(convites_qs):
    return {
        "total": convites_qs.count(),
        "novos": convites_qs.filter(estado=TokenAcesso.Estado.NOVO).count(),
        "usados": convites_qs.filter(estado=TokenAcesso.Estado.USADO).count(),
        "expirados": convites_qs.filter(estado=TokenAcesso.Estado.EXPIRADO).count(),
        "revogados": convites_qs.filter(estado=TokenAcesso.Estado.REVOGADO).count(),
    }


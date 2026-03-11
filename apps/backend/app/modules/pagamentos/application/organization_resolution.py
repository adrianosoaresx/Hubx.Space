from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from django.db.models import Q
from django.http import HttpRequest

from organizacoes.models import Organizacao


def _resolver_por_host(host: str) -> Organizacao | None:
    normalized_host = (host or "").split(":")[0].lower()
    if not normalized_host:
        return None

    subdomain = normalized_host.split(".")[0]
    org = (
        Organizacao.objects.filter(
            Q(nome_site__iexact=subdomain)
            | Q(nome_site__iexact=normalized_host)
            | Q(site__icontains=normalized_host)
        ).first()
    )
    if org:
        return org

    for candidate in Organizacao.objects.exclude(site="").iterator():
        netloc = urlparse(candidate.site).netloc.lower()
        if netloc and (normalized_host == netloc or normalized_host.endswith(netloc)):
            return candidate
    return None


def obter_organizacao_checkout(
    request: HttpRequest, organizacao_id: str | None = None
) -> Organizacao | None:
    raw_id = organizacao_id or request.POST.get("organizacao_id") or request.GET.get("organizacao_id")
    if raw_id:
        try:
            org = Organizacao.objects.filter(id=raw_id).first()
            if org:
                return org
        except (ValueError, TypeError):
            pass
    return _resolver_por_host(request.get_host() or "")


def obter_organizacao_webhook(
    request: HttpRequest,
    _payload: dict[str, Any],
    transacao: Any | None,
) -> Organizacao | None:
    if transacao and getattr(transacao.pedido, "organizacao_id", None):
        return transacao.pedido.organizacao
    return _resolver_por_host(request.get_host() or "")

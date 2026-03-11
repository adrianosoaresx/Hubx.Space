from __future__ import annotations

from django.utils.http import url_has_allowed_host_and_scheme

from accounts.mfa import get_available_mfa_methods, resolve_preferred_method


def user_requires_mfa(user) -> bool:
    return bool(get_available_mfa_methods(user))


def get_validated_redirect_url(request, fallback_url: str | None = None) -> str | None:
    redirect_url = request.POST.get("next") or request.GET.get("next")
    if redirect_url and url_has_allowed_host_and_scheme(
        url=redirect_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect_url
    return fallback_url


def resolve_pending_2fa_method(session, user) -> tuple[str | None, list[str], bool]:
    methods = get_available_mfa_methods(user)
    if not methods:
        return None, [], False
    current = session.get("pending_2fa_method")
    changed = False
    if current not in methods:
        current = resolve_preferred_method(user, methods)
        session["pending_2fa_method"] = current
        changed = True
    return current, methods, changed


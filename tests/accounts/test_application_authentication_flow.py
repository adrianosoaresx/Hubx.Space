import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.accounts.application.authentication_flow import (  # noqa: E402
    build_pending_2fa_session_data,
    resolve_2fa_success_redirect,
)


def test_build_pending_2fa_session_data():
    data = build_pending_2fa_session_data(
        user_id=10,
        next_url="/destino/",
        method="totp",
    )

    assert data.user_id == 10
    assert data.next_url == "/destino/"
    assert data.method == "totp"


def test_resolve_2fa_success_redirect_prioritizes_explicit():
    url = resolve_2fa_success_redirect(
        explicit_next_url="/explicito/",
        session_next_url="/sessao/",
        fallback_url="/fallback/",
    )
    assert url == "/explicito/"


def test_resolve_2fa_success_redirect_falls_back_to_session():
    url = resolve_2fa_success_redirect(
        explicit_next_url=None,
        session_next_url="/sessao/",
        fallback_url="/fallback/",
    )
    assert url == "/sessao/"

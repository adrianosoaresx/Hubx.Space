import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.notificacoes.application.dropdown_targets import (
    resolve_dropdown_target_url,
)


def test_resolve_dropdown_target_url_feed_com_post_id():
    result = resolve_dropdown_target_url(
        template_code="feed_like",
        context={"post_id": 12},
        default_target_url="/notificacoes/minhas/",
        feed_target_builder=lambda post_id: f"/feed/posts/{post_id}#post-{post_id}",
    )

    assert result == "/feed/posts/12#post-12"


def test_resolve_dropdown_target_url_connection_com_actor_id():
    result = resolve_dropdown_target_url(
        template_code="connection_request",
        context={"actor_id": 55},
        default_target_url="/notificacoes/minhas/",
        feed_target_builder=lambda post_id: f"/feed/posts/{post_id}#post-{post_id}",
    )

    assert result == "/perfil/55"


def test_resolve_dropdown_target_url_fallback():
    result = resolve_dropdown_target_url(
        template_code="email_confirmation",
        context={},
        default_target_url="/notificacoes/minhas/",
        feed_target_builder=lambda post_id: f"/feed/posts/{post_id}#post-{post_id}",
    )

    assert result == "/notificacoes/minhas/"

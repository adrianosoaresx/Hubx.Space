import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.conexoes.application.connection_notifications import (
    build_connection_notification_context,
    resolve_connection_template,
)


def test_resolve_connection_template_por_evento():
    assert resolve_connection_template("request") == "connection_request"
    assert resolve_connection_template("accepted") == "connection_accepted"
    assert resolve_connection_template("declined") == "connection_declined"


def test_resolve_connection_template_default():
    assert resolve_connection_template("desconhecido") == "connection_request"


def test_build_connection_notification_context_request():
    context = build_connection_notification_context(
        event_key="request",
        actor_display_name="Ana",
        actor_id="12",
    )
    assert context == {"solicitante": "Ana", "actor_id": "12"}


def test_build_connection_notification_context_decision():
    context = build_connection_notification_context(
        event_key="accepted",
        actor_display_name="Ana",
        actor_id="12",
    )
    assert context == {"solicitado": "Ana", "actor_id": "12"}

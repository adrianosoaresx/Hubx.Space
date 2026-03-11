from __future__ import annotations

CONNECTION_NOTIFICATION_TEMPLATES = {
    "request": "connection_request",
    "accepted": "connection_accepted",
    "declined": "connection_declined",
}


def resolve_connection_template(event_key: str) -> str:
    return CONNECTION_NOTIFICATION_TEMPLATES.get(
        event_key, CONNECTION_NOTIFICATION_TEMPLATES["request"]
    )


def build_connection_notification_context(
    *, event_key: str, actor_display_name: str, actor_id: str
) -> dict[str, str]:
    if event_key == "request":
        return {"solicitante": actor_display_name, "actor_id": actor_id}
    return {"solicitado": actor_display_name, "actor_id": actor_id}

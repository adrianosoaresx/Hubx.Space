from __future__ import annotations

INTERACTION_NOTIFICATION_TEMPLATES = {
    "like": "feed_like",
    "comment": "feed_comment",
    "share": "feed_share",
}


def resolve_interaction_template(interaction_type: str) -> str:
    return INTERACTION_NOTIFICATION_TEMPLATES.get(
        interaction_type, INTERACTION_NOTIFICATION_TEMPLATES["comment"]
    )


def build_interaction_notification_context(
    *, post_id: str, interaction_type: str
) -> dict[str, str]:
    return {
        "post_id": str(post_id),
        "interaction_type": interaction_type,
    }

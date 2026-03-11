from __future__ import annotations

from typing import Any, Mapping, Callable


def resolve_dropdown_target_url(
    *,
    template_code: str,
    context: Mapping[str, Any],
    default_target_url: str,
    feed_target_builder: Callable[[Any], str],
) -> str:
    if template_code.startswith("feed_"):
        post_id = context.get("post_id")
        if post_id:
            return feed_target_builder(post_id)
        return default_target_url

    if template_code.startswith("connection_"):
        actor_id = context.get("actor_id") or context.get("user_id")
        if actor_id:
            return f"/perfil/{actor_id}"
        return default_target_url

    return default_target_url

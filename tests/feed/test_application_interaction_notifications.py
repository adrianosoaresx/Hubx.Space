import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.feed.application.interaction_notifications import (
    build_interaction_notification_context,
    resolve_interaction_template,
)


def test_resolve_interaction_template_por_tipo():
    assert resolve_interaction_template("like") == "feed_like"
    assert resolve_interaction_template("comment") == "feed_comment"
    assert resolve_interaction_template("share") == "feed_share"


def test_resolve_interaction_template_default():
    assert resolve_interaction_template("unknown") == "feed_comment"


def test_build_interaction_notification_context():
    context = build_interaction_notification_context(
        post_id="post-1",
        interaction_type="like",
    )
    assert context == {"post_id": "post-1", "interaction_type": "like"}

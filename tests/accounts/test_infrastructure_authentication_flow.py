import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.accounts.infrastructure.authentication_flow import (  # noqa: E402
    DjangoPending2FASessionManager,
)


class _FakeSession(dict):
    modified = False


def test_pending_2fa_session_manager_set_and_clear_helpers():
    session = _FakeSession()
    manager = DjangoPending2FASessionManager()

    manager.set_pending(session=session, user_id=42, next_url="/destino/", method="totp")
    assert session[manager.KEY_USER_ID] == 42
    assert session[manager.KEY_NEXT_URL] == "/destino/"
    assert session[manager.KEY_METHOD] == "totp"

    manager.set_challenge_id(session=session, challenge_id="abc-123")
    assert manager.get_challenge_id(session=session) == "abc-123"

    manager.set_method(session=session, method="email_otp")
    assert session[manager.KEY_METHOD] == "email_otp"
    assert manager.get_next_url(session=session) == "/destino/"

    manager.clear_challenge_id(session=session)
    assert manager.get_challenge_id(session=session) is None

    manager.clear_pending(session=session)
    assert manager.KEY_USER_ID not in session
    assert manager.KEY_NEXT_URL not in session
    assert manager.KEY_METHOD not in session
    assert manager.KEY_CHALLENGE_ID not in session

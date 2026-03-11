from __future__ import annotations

from django.contrib.auth import login as django_login

from accounts.auth import clear_login_failures, get_user_lockout_until
from accounts.mfa import has_blocking_mfa_misconfiguration
from accounts.models import LoginAttempt


class DjangoPending2FASessionManager:
    KEY_USER_ID = "pending_2fa_user_id"
    KEY_NEXT_URL = "pending_2fa_next_url"
    KEY_METHOD = "pending_2fa_method"
    KEY_CHALLENGE_ID = "pending_2fa_challenge_id"

    def set_pending(self, *, session, user_id: int, next_url: str | None, method: str | None) -> None:
        session[self.KEY_USER_ID] = user_id
        session[self.KEY_NEXT_URL] = next_url
        session[self.KEY_METHOD] = method
        session.pop(self.KEY_CHALLENGE_ID, None)
        session.modified = True

    def clear_pending(self, *, session) -> None:
        session.pop(self.KEY_USER_ID, None)
        session.pop(self.KEY_NEXT_URL, None)
        session.pop(self.KEY_METHOD, None)
        session.pop(self.KEY_CHALLENGE_ID, None)
        session.modified = True

    def set_method(self, *, session, method: str | None) -> None:
        session[self.KEY_METHOD] = method
        session.modified = True

    def get_next_url(self, *, session) -> str | None:
        return session.get(self.KEY_NEXT_URL)

    def set_challenge_id(self, *, session, challenge_id: str) -> None:
        session[self.KEY_CHALLENGE_ID] = challenge_id
        session.modified = True

    def get_challenge_id(self, *, session) -> str | None:
        return session.get(self.KEY_CHALLENGE_ID)

    def clear_challenge_id(self, *, session) -> None:
        session.pop(self.KEY_CHALLENGE_ID, None)
        session.modified = True


class DjangoLoginSuccessService:
    def register_success(self, *, user, request, ip: str | None) -> None:
        django_login(request, user, backend="accounts.backends.EmailBackend")
        clear_login_failures(user)
        LoginAttempt.objects.create(
            usuario=user,
            email=user.email,
            sucesso=True,
            ip=ip,
        )


class DjangoPending2FAUserResolver:
    def __init__(self, *, user_model, session_manager: DjangoPending2FASessionManager) -> None:
        self._user_model = user_model
        self._session_manager = session_manager

    def resolve_valid_user(self, *, session, user_requires_mfa) -> object | None:
        user_id = session.get(self._session_manager.KEY_USER_ID)
        if not user_id:
            return None

        try:
            user = self._user_model.objects.get(pk=user_id)
        except self._user_model.DoesNotExist:
            self._session_manager.clear_pending(session=session)
            return None

        if not user.is_active:
            self._session_manager.clear_pending(session=session)
            return None
        if get_user_lockout_until(user):
            self._session_manager.clear_pending(session=session)
            return None
        if has_blocking_mfa_misconfiguration(user):
            self._session_manager.clear_pending(session=session)
            return None
        if not user_requires_mfa(user):
            self._session_manager.clear_pending(session=session)
            return None
        return user

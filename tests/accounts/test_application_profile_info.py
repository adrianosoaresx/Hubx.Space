import os
from types import SimpleNamespace

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.accounts.application.profile_info import ProfileInfoUseCase  # noqa: E402


class _FakeForm:
    def __init__(self, *, is_valid: bool, email_changed: bool = False):
        self._is_valid = is_valid
        self.email_changed = email_changed
        self.saved = False

    def is_valid(self) -> bool:
        return self._is_valid

    def save(self):
        self.saved = True


class _FakeGateway:
    def __init__(self, *, bound_form: _FakeForm, unbound_form: _FakeForm):
        self.bound_form = bound_form
        self.unbound_form = unbound_form

    def create_bound(self, *, data, files, instance):
        return self.bound_form

    def create_unbound(self, *, instance):
        return self.unbound_form


def test_profile_info_use_case_submit_success():
    gateway = _FakeGateway(
        bound_form=_FakeForm(is_valid=True, email_changed=True),
        unbound_form=_FakeForm(is_valid=True),
    )
    use_case = ProfileInfoUseCase(form_gateway=gateway)

    result = use_case.submit(data={}, files={}, target_user=SimpleNamespace())

    assert result.success is True
    assert result.email_changed is True
    assert result.form.saved is True


def test_profile_info_use_case_submit_invalid():
    gateway = _FakeGateway(
        bound_form=_FakeForm(is_valid=False),
        unbound_form=_FakeForm(is_valid=True),
    )
    use_case = ProfileInfoUseCase(form_gateway=gateway)

    result = use_case.submit(data={}, files={}, target_user=SimpleNamespace())

    assert result.success is False
    assert result.email_changed is False
    assert result.form.saved is False


def test_profile_info_feedback_messages():
    info_self = ProfileInfoUseCase.build_success_feedback(
        email_changed=True,
        is_self=True,
        target_display_name="Alvo",
    )
    success_other = ProfileInfoUseCase.build_success_feedback(
        email_changed=False,
        is_self=False,
        target_display_name="Alvo",
    )

    assert info_self == ("info", "Confirme o novo e-mail enviado.")
    assert success_other == ("success", "Informações do perfil de Alvo atualizadas.")

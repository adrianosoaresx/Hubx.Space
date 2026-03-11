import os
from types import SimpleNamespace

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.accounts.application.profile_permissions import (
    can_manage_profile,
    can_promote_profile,
)


def _user(**kwargs):
    data = {
        "is_authenticated": True,
        "organizacao_id": 1,
        "get_tipo_usuario": "admin",
    }
    data.update(kwargs)
    return SimpleNamespace(**data)


def _profile(**kwargs):
    data = {
        "organizacao_id": 1,
        "get_tipo_usuario": "nucleado",
    }
    data.update(kwargs)
    return SimpleNamespace(**data)


def test_can_manage_profile_same_org_admin():
    viewer = _user(get_tipo_usuario="admin", organizacao_id=10)
    profile = _profile(organizacao_id=10)
    assert can_manage_profile(viewer, profile) is True


def test_can_manage_profile_different_org_admin():
    viewer = _user(get_tipo_usuario="admin", organizacao_id=10)
    profile = _profile(organizacao_id=20)
    assert can_manage_profile(viewer, profile) is False


def test_can_promote_profile_allowed_for_operator_same_org():
    viewer = _user(get_tipo_usuario="operador", organizacao_id=3)
    profile = _profile(organizacao_id=3, get_tipo_usuario="nucleado")
    assert can_promote_profile(viewer, profile) is True


def test_can_promote_profile_denied_for_admin_target():
    viewer = _user(get_tipo_usuario="admin", organizacao_id=3)
    profile = _profile(organizacao_id=3, get_tipo_usuario="admin")
    assert can_promote_profile(viewer, profile) is False

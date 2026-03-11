import os
from types import SimpleNamespace

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.organizacoes.application.access_policy import (  # noqa: E402
    apply_admin_org_scope,
    apply_user_org_scope,
)


class _FakeQS:
    def __init__(self):
        self.filters = []

    def filter(self, **kwargs):
        self.filters.append(kwargs)
        return self


def test_apply_admin_org_scope_filters_for_admin():
    qs = _FakeQS()
    user = SimpleNamespace(user_type="admin", organizacao_id="org-1")
    apply_admin_org_scope(qs, user)
    assert qs.filters == [{"pk": "org-1"}]


def test_apply_admin_org_scope_no_filter_for_non_admin():
    qs = _FakeQS()
    user = SimpleNamespace(user_type="nucleado", organizacao_id="org-1")
    apply_admin_org_scope(qs, user)
    assert qs.filters == []


def test_apply_user_org_scope_filters_when_org_exists():
    qs = _FakeQS()
    user = SimpleNamespace(organizacao_id="org-2")
    apply_user_org_scope(qs, user)
    assert qs.filters == [{"pk": "org-2"}]


import os
from types import SimpleNamespace

import django
import pytest
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from accounts.models import UserType
from apps.backend.app.modules.eventos.application.event_write_policy import (
    apply_coordinator_nucleo_scope,
    build_evento_change_details,
    ensure_coordinator_can_use_nucleo,
    ensure_user_can_create_evento,
)
from organizacoes.models import Organizacao


class _FakeQuerySet:
    def __init__(self):
        self.filter_kwargs = None
        self.none_called = False

    def filter(self, **kwargs):
        self.filter_kwargs = kwargs
        return self

    def none(self):
        self.none_called = True
        return self


def test_ensure_user_can_create_evento_blocks_root():
    with pytest.raises(PermissionDenied):
        ensure_user_can_create_evento(UserType.ROOT.value)


def test_ensure_user_can_create_evento_allows_admin():
    ensure_user_can_create_evento(UserType.ADMIN.value)


def test_ensure_coordinator_can_use_nucleo_rejects_foreign_nucleo():
    with pytest.raises(PermissionDenied):
        ensure_coordinator_can_use_nucleo(
            user_type=UserType.COORDENADOR.value,
            allowed_nucleo_ids=[1, 2],
            nucleo_id=9,
        )


def test_ensure_coordinator_can_use_nucleo_allows_known_nucleo():
    ensure_coordinator_can_use_nucleo(
        user_type=UserType.COORDENADOR.value,
        allowed_nucleo_ids=[1, 2],
        nucleo_id=2,
    )


def test_apply_coordinator_nucleo_scope_without_ids_returns_none_queryset():
    queryset = _FakeQuerySet()

    scoped = apply_coordinator_nucleo_scope(
        queryset,
        user_type=UserType.COORDENADOR.value,
        allowed_nucleo_ids=[],
    )

    assert scoped is queryset
    assert queryset.none_called is True


def test_apply_coordinator_nucleo_scope_with_ids_applies_filter():
    queryset = _FakeQuerySet()

    scoped = apply_coordinator_nucleo_scope(
        queryset,
        user_type=UserType.COORDENADOR.value,
        allowed_nucleo_ids=[10, 20],
    )

    assert scoped is queryset
    assert queryset.filter_kwargs == {"nucleo_id__in": [10, 20]}


def test_apply_coordinator_nucleo_scope_non_coordinator_keeps_queryset():
    queryset = _FakeQuerySet()

    scoped = apply_coordinator_nucleo_scope(
        queryset,
        user_type=UserType.ADMIN.value,
        allowed_nucleo_ids=[],
    )

    assert scoped is queryset
    assert queryset.filter_kwargs is None
    assert queryset.none_called is False


@pytest.mark.django_db
def test_build_evento_change_details_serializes_values():
    org_before = Organizacao.objects.create(nome="Org Antes", cnpj="52345678000195")
    org_after = Organizacao.objects.create(nome="Org Depois", cnpj="62345678000195")
    old_obj = SimpleNamespace(
        titulo=_("Titulo antigo"),
        organizacao=org_before,
        tags=["a", "b"],
        qtd=1,
    )
    cleaned_data = {
        "titulo": "Titulo novo",
        "organizacao": org_after,
        "tags": ["a", "c"],
        "qtd": 1,
    }

    details = build_evento_change_details(
        old_obj=old_obj,
        cleaned_data=cleaned_data,
        changed_fields=["titulo", "organizacao", "tags", "qtd"],
    )

    assert details["titulo"] == {"antes": "Titulo antigo", "depois": "Titulo novo"}
    assert details["organizacao"]["antes"]["id"] == org_before.id
    assert details["organizacao"]["depois"]["id"] == org_after.id
    assert details["tags"] == {"antes": ["a", "b"], "depois": ["a", "c"]}
    assert "qtd" not in details

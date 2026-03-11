import os
from types import SimpleNamespace

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from accounts.models import UserType
from apps.backend.app.modules.eventos.application.visibility import (
    can_manage_event_portfolio,
    can_view_event_subscribers,
    get_nucleos_coordenacao_consultoria_ids,
    get_tipo_usuario,
    has_restricted_event_access,
    is_guest_user,
    is_user_event_coordinator,
    resolve_planejamento_permissions,
)


class _MockRelatedManager:
    def __init__(self, ids):
        self._ids = ids

    def filter(self, **kwargs):
        return self

    def values_list(self, *_args, **_kwargs):
        return self._ids


class _MockParticipacoesManager:
    def __init__(self, exists_result: bool):
        self.exists_result = exists_result

    def filter(self, **kwargs):
        return SimpleNamespace(exists=lambda: self.exists_result)


def test_get_tipo_usuario_retorna_string():
    user = SimpleNamespace(get_tipo_usuario=UserType.ADMIN.value)
    assert get_tipo_usuario(user) == UserType.ADMIN.value


def test_is_guest_user():
    user = SimpleNamespace(get_tipo_usuario=UserType.CONVIDADO.value)
    assert is_guest_user(user) is True


def test_get_nucleos_coordenacao_consultoria_ids_agrega_fontes():
    user = SimpleNamespace(
        nucleo_id=10,
        participacoes=_MockRelatedManager([11, 12]),
        nucleos_consultoria=_MockRelatedManager([13]),
    )

    ids = get_nucleos_coordenacao_consultoria_ids(user)

    assert ids == {10, 11, 12, 13}


def test_resolve_planejamento_permissions_para_coordenador():
    user = SimpleNamespace(
        get_tipo_usuario=UserType.COORDENADOR.value,
        nucleo_id=7,
        participacoes=_MockRelatedManager([]),
        nucleos_consultoria=_MockRelatedManager([]),
    )

    can_view, nucleo_ids_limit = resolve_planejamento_permissions(user)

    assert can_view is True
    assert nucleo_ids_limit == {7}


def test_is_user_event_coordinator_true_by_participacao():
    user = SimpleNamespace(
        participacoes=_MockParticipacoesManager(True),
        nucleo_id=1,
        is_coordenador=False,
    )
    evento = SimpleNamespace(nucleo_id=9, nucleo=SimpleNamespace(id=9))

    assert is_user_event_coordinator(user, evento) is True


def test_is_user_event_coordinator_true_by_direct_nucleo():
    user = SimpleNamespace(
        participacoes=_MockParticipacoesManager(False),
        nucleo_id=7,
        is_coordenador=True,
    )
    evento = SimpleNamespace(nucleo_id=7, nucleo=SimpleNamespace(id=7))

    assert is_user_event_coordinator(user, evento) is True


def test_has_restricted_event_access_for_coordinator():
    user = SimpleNamespace(
        get_tipo_usuario=UserType.COORDENADOR.value,
        participacoes=_MockParticipacoesManager(True),
        nucleo_id=None,
        is_coordenador=False,
    )
    evento = SimpleNamespace(nucleo_id=2, nucleo=SimpleNamespace(id=2))
    assert has_restricted_event_access(user, evento) is True


def test_can_manage_event_portfolio_for_user_with_permission():
    user = SimpleNamespace(
        get_tipo_usuario=UserType.NUCLEADO.value,
        has_perm=lambda perm: perm == "eventos.change_evento",
        participacoes=_MockParticipacoesManager(False),
        nucleo_id=None,
        is_coordenador=False,
    )
    evento = SimpleNamespace(nucleo_id=3, nucleo=SimpleNamespace(id=3))
    assert can_manage_event_portfolio(user, evento) is True


def test_can_view_event_subscribers_delegates_restricted_access():
    user = SimpleNamespace(
        get_tipo_usuario=UserType.ADMIN.value,
        has_perm=lambda _perm: False,
        participacoes=_MockParticipacoesManager(False),
        nucleo_id=None,
        is_coordenador=False,
    )
    evento = SimpleNamespace(nucleo_id=3, nucleo=SimpleNamespace(id=3))
    assert can_view_event_subscribers(user, evento) is True

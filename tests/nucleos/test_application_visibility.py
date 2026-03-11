import os
from types import SimpleNamespace

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.nucleos.application.visibility import (  # noqa: E402
    get_allowed_classificacao_keys,
    get_consultor_nucleo_ids,
    user_can_manage_nucleacao_requests,
    user_has_consultoria_access,
)


class _ExistsManager:
    def __init__(self, exists_value):
        self._exists_value = exists_value

    def filter(self, **kwargs):
        return self

    def exists(self):
        return self._exists_value


class _ValuesListManager:
    def __init__(self, values):
        self._values = values

    def filter(self, **kwargs):
        return self

    def values_list(self, *args, **kwargs):
        return self._values

    def exists(self):
        return bool(self._values)


def test_user_has_consultoria_access_by_type():
    user = SimpleNamespace(get_tipo_usuario="consultor", user_type="consultor", nucleos_consultoria=None)
    assert user_has_consultoria_access(user) is True


def test_get_consultor_nucleo_ids_aggregates_sources():
    user = SimpleNamespace(
        nucleos_consultoria=_ValuesListManager([1, 2]),
        participacoes=_ValuesListManager([2, 3]),
        nucleo_id=4,
    )
    assert get_consultor_nucleo_ids(user) == {1, 2, 3, 4}


def test_get_allowed_classificacao_keys_for_nucleado_is_constituido_only():
    user = SimpleNamespace(get_tipo_usuario="nucleado", user_type="nucleado", nucleos_consultoria=None)
    keys = get_allowed_classificacao_keys(user)
    assert keys == {"constituido"}


def test_user_can_manage_nucleacao_requests_admin_same_org():
    user = SimpleNamespace(get_tipo_usuario="admin", organizacao_id="org-1")
    nucleo = SimpleNamespace(organizacao_id="org-1", pk=10)
    assert user_can_manage_nucleacao_requests(user, nucleo) is True


def test_user_can_manage_nucleacao_requests_consultor_with_scope():
    user = SimpleNamespace(get_tipo_usuario="consultor", organizacao_id="org-1")
    nucleo = SimpleNamespace(organizacao_id="org-1", pk=20)
    assert user_can_manage_nucleacao_requests(user, nucleo, consultor_ids={20, 21}) is True


def test_user_can_manage_nucleacao_requests_coordenador_needs_active_participacao():
    participacoes = _ExistsManager(True)
    user = SimpleNamespace(get_tipo_usuario="coordenador", organizacao_id="org-1")
    nucleo = SimpleNamespace(organizacao_id="org-1", pk=20, participacoes=participacoes)
    assert user_can_manage_nucleacao_requests(user, nucleo) is True


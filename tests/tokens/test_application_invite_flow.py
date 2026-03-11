import os

import django
from django.test import RequestFactory

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.tokens.application.invite_flow import (  # noqa: E402
    build_invite_totals,
    get_query_param,
)
from tokens.models import TokenAcesso  # noqa: E402


class _FakeQS:
    def __init__(self, values):
        self._values = values

    def count(self):
        return self._values.get("total", 0)

    def filter(self, **kwargs):
        estado = kwargs.get("estado")
        map_key = {
            TokenAcesso.Estado.NOVO: "novos",
            TokenAcesso.Estado.USADO: "usados",
            TokenAcesso.Estado.EXPIRADO: "expirados",
            TokenAcesso.Estado.REVOGADO: "revogados",
        }.get(estado, "total")
        return _FakeQS({"total": self._values.get(map_key, 0)})


def test_build_invite_totals_maps_states():
    qs = _FakeQS(
        {
            "total": 10,
            "novos": 4,
            "usados": 3,
            "expirados": 2,
            "revogados": 1,
        }
    )
    totals = build_invite_totals(qs)
    assert totals == {
        "total": 10,
        "novos": 4,
        "usados": 3,
        "expirados": 2,
        "revogados": 1,
    }


def test_get_query_param_supports_amp_prefix():
    request = RequestFactory().get("/tokens/?amp;token=abc")
    assert get_query_param(request, "token") == "abc"

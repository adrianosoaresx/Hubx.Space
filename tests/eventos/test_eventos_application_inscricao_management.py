import os
from types import SimpleNamespace

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from accounts.models import UserType
from apps.backend.app.modules.eventos.application.inscricao_management import (
    build_inscricao_form_kwargs,
    build_inscricao_update_context,
    build_inscricao_update_queryset,
    can_toggle_pagamento_validacao,
    resolve_inscricao_valor_pago,
    toggle_pagamento_validado_status,
)


class _FakeQuerySet:
    def __init__(self):
        self.related = None
        self.filter_kwargs = None

    def select_related(self, *args):
        self.related = args
        return self

    def filter(self, **kwargs):
        self.filter_kwargs = kwargs
        return self


def test_build_inscricao_update_queryset_applies_related_and_filter():
    base_qs = _FakeQuerySet()
    eventos_qs = object()

    result = build_inscricao_update_queryset(base_qs, eventos_qs)

    assert result is base_qs
    assert base_qs.related == ("evento", "user")
    assert base_qs.filter_kwargs == {"evento__in": eventos_qs}


def test_build_inscricao_form_kwargs_reads_evento_and_user():
    inscricao = SimpleNamespace(evento="EVENTO", user="USER")

    kwargs = build_inscricao_form_kwargs(inscricao)

    assert kwargs == {"evento": "EVENTO", "user": "USER"}


def test_build_inscricao_update_context_payload():
    evento = SimpleNamespace(descricao="Descricao teste")

    context = build_inscricao_update_context(
        evento=evento,
        back_href="/eventos/1/",
        valor_evento_usuario=99.9,
    )

    assert context["evento"] is evento
    assert str(context["title"]) == "Editar inscrição"
    assert context["subtitle"] == "Descricao teste"
    assert context["back_href"] == "/eventos/1/"
    assert context["valor_evento_usuario"] == 99.9
    assert context["show_comprovante_pagamento"] is True


def test_resolve_inscricao_valor_pago_prioritizes_event_value():
    assert resolve_inscricao_valor_pago(valor_evento_usuario=120, valor_pago_atual=10) == 120
    assert resolve_inscricao_valor_pago(valor_evento_usuario=None, valor_pago_atual=10) == 10


def test_can_toggle_pagamento_validacao_accepts_only_admin_or_operador_same_org():
    assert can_toggle_pagamento_validacao(
        tipo_usuario=UserType.ADMIN.value,
        user_organizacao_id="org-1",
        evento_organizacao_id="org-1",
    )
    assert can_toggle_pagamento_validacao(
        tipo_usuario=UserType.OPERADOR.value,
        user_organizacao_id="org-1",
        evento_organizacao_id="org-1",
    )
    assert not can_toggle_pagamento_validacao(
        tipo_usuario=UserType.COORDENADOR.value,
        user_organizacao_id="org-1",
        evento_organizacao_id="org-1",
    )
    assert not can_toggle_pagamento_validacao(
        tipo_usuario=UserType.ADMIN.value,
        user_organizacao_id="org-1",
        evento_organizacao_id="org-2",
    )


def test_toggle_pagamento_validado_status_inverts_boolean():
    assert toggle_pagamento_validado_status(pagamento_validado_atual=True) is False
    assert toggle_pagamento_validado_status(pagamento_validado_atual=False) is True

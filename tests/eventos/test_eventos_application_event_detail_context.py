import os
from decimal import Decimal
from types import SimpleNamespace

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from accounts.models import UserType
from apps.backend.app.modules.eventos.application.event_detail_context import (
    build_financeiro_summary,
    build_inscricao_status_summary,
    resolve_event_management_permissions,
    sort_inscricoes_financeiro,
)


def _build_inscricao(
    *,
    status: str,
    pagamento_validado: bool,
    contato: str = "",
    username: str = "",
    valor_pago=None,
    valor_evento=None,
):
    user = SimpleNamespace(
        contato=contato,
        display_name="",
        get_full_name=lambda: "",
        username=username,
    )
    return SimpleNamespace(
        status=status,
        pagamento_validado=pagamento_validado,
        user=user,
        valor_pago=valor_pago,
        get_valor_evento=lambda: valor_evento,
    )


def test_resolve_event_management_permissions_for_admin():
    permissions = resolve_event_management_permissions(
        tipo_usuario=UserType.ADMIN.value,
        user_has_change_perm=False,
        user_has_delete_perm=False,
        coordenador_do_evento=False,
    )

    assert permissions["pode_editar_evento"] is True
    assert permissions["pode_excluir_evento"] is True
    assert permissions["pode_gerenciar_inscricoes"] is True
    assert permissions["pode_ver_financeiro"] is True
    assert permissions["pode_gerenciar_convites"] is True


def test_resolve_event_management_permissions_for_coordinator_event_owner():
    permissions = resolve_event_management_permissions(
        tipo_usuario=UserType.COORDENADOR.value,
        user_has_change_perm=False,
        user_has_delete_perm=False,
        coordenador_do_evento=True,
    )

    assert permissions["pode_editar_evento"] is True
    assert permissions["pode_excluir_evento"] is True
    assert permissions["pode_ver_financeiro"] is False


def test_sort_inscricoes_financeiro_filters_cancelled_and_orders():
    inscricoes = [
        _build_inscricao(status="confirmada", pagamento_validado=False, contato="Beta"),
        _build_inscricao(status="cancelada", pagamento_validado=False, contato="Alpha"),
        _build_inscricao(status="pendente", pagamento_validado=False, contato="Gamma"),
    ]

    ordered = sort_inscricoes_financeiro(inscricoes)

    assert len(ordered) == 2
    assert [ins.user.contato for ins in ordered] == ["Beta", "Gamma"]


def test_build_inscricao_status_summary_with_capacity():
    inscricoes = [
        _build_inscricao(status="confirmada", pagamento_validado=True),
        _build_inscricao(status="confirmada", pagamento_validado=False),
        _build_inscricao(status="pendente", pagamento_validado=False),
        _build_inscricao(status="cancelada", pagamento_validado=False),
    ]

    summary = build_inscricao_status_summary(inscricoes=inscricoes, participantes_maximo=5)

    assert summary["total_inscricoes_confirmadas"] == 2
    assert summary["total_inscricoes_pendentes"] == 1
    assert summary["total_inscricoes_canceladas"] == 1
    assert summary["vagas_disponiveis"] == 3


def test_build_financeiro_summary_counts_and_sums():
    inscricoes_financeiro = [
        _build_inscricao(
            status="confirmada",
            pagamento_validado=True,
            valor_pago=Decimal("10.50"),
            valor_evento=Decimal("11.00"),
        ),
        _build_inscricao(
            status="pendente",
            pagamento_validado=True,
            valor_pago=None,
            valor_evento=Decimal("20.00"),
        ),
        _build_inscricao(
            status="pendente",
            pagamento_validado=False,
            valor_pago=Decimal("99.99"),
            valor_evento=Decimal("99.99"),
        ),
    ]

    summary = build_financeiro_summary(inscricoes_financeiro)

    assert summary["total_pagamentos_validados"] == 2
    assert summary["total_pagamentos_pendentes"] == 1
    assert summary["valor_total_pagamentos_validados"] == Decimal("30.50")

import os
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.pagamentos.application.checkout_inscricao_flow import (  # noqa: E402
    build_checkout_initial_from_inscricao,
)


def test_build_checkout_initial_from_inscricao_with_valor():
    evento = SimpleNamespace(
        organizacao_id=15,
        get_valor_para_usuario=lambda user: Decimal("90.00"),
    )
    inscricao = SimpleNamespace(
        uuid=uuid4(),
        evento=evento,
    )
    user = SimpleNamespace(id=2)

    initial = build_checkout_initial_from_inscricao(inscricao=inscricao, user=user)

    assert initial["inscricao_uuid"] == inscricao.uuid
    assert initial["organizacao_id"] == 15
    assert initial["valor"] == Decimal("90.00")

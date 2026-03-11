from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4
import os

import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.pagamentos.application.faturamento_checkout_use_case import (
    build_faturamento_checkout_input,
    execute_faturamento_checkout_use_case,
)
@pytest.mark.django_db
def test_build_faturamento_checkout_input_normaliza_campos():
    checkout_input = build_faturamento_checkout_input(
        cleaned_data={
            "inscricao_uuid": "  123  ",
            "condicao_faturamento": " 2x ",
        }
    )
    assert checkout_input.inscricao_uuid == "123"
    assert checkout_input.condicao_faturamento == "2x"


@pytest.mark.django_db
def test_execute_faturamento_checkout_use_case_sucesso():
    result = execute_faturamento_checkout_use_case(
        checkout_input=build_faturamento_checkout_input(
            cleaned_data={"inscricao_uuid": str(uuid4()), "condicao_faturamento": "2x"}
        ),
        registrar_faturamento=lambda _uuid, _condicao: SimpleNamespace(uuid=uuid4()),
    )

    assert result.success is True
    assert result.error_message is None
    assert result.redirect_url is not None
    assert "/eventos/inscricoes/" in result.redirect_url
    assert "status=info" in result.redirect_url


@pytest.mark.django_db
def test_execute_faturamento_checkout_use_case_erro_quando_inscricao_nao_encontrada():
    result = execute_faturamento_checkout_use_case(
        checkout_input=build_faturamento_checkout_input(
            cleaned_data={"inscricao_uuid": str(uuid4()), "condicao_faturamento": "2x"}
        ),
        registrar_faturamento=lambda _uuid, _condicao: None,
    )

    assert result.success is False
    assert result.redirect_url is None
    assert "Não foi possível localizar a inscrição" in str(result.error_message)

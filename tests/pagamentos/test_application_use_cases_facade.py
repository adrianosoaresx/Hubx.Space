from __future__ import annotations

import os
from uuid import uuid4

import django
from payments import PaymentStatus

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.pagamentos import application as pagamentos_application


def test_application_use_cases_facade_exports_expected_symbols():
    expected = {
        "build_faturamento_checkout_input",
        "execute_faturamento_checkout_use_case",
        "execute_pix_checkout_use_case",
        "mapear_status_pagamento",
        "normalizar_uuid",
        "obter_organizacao_checkout",
        "obter_organizacao_webhook",
    }
    assert expected.issubset(set(pagamentos_application.__all__))


def test_application_use_cases_facade_reuses_transaction_helpers():
    generated = uuid4()
    assert pagamentos_application.normalizar_uuid(str(generated)) == generated
    assert (
        pagamentos_application.mapear_status_pagamento(PaymentStatus.CONFIRMED)
        == "approved"
    )

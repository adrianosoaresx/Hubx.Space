import os
from uuid import uuid4

import django
from payments import PaymentStatus

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.pagamentos.application.transaction_mapping import (
    mapear_status_pagamento,
    normalizar_uuid,
)
from pagamentos.models import Transacao


def test_mapear_status_pagamento_retorna_aprovada():
    assert mapear_status_pagamento(PaymentStatus.CONFIRMED) == Transacao.Status.APROVADA


def test_mapear_status_pagamento_retorna_estornada():
    assert mapear_status_pagamento(PaymentStatus.REFUNDED) == Transacao.Status.ESTORNADA


def test_mapear_status_pagamento_retorna_falhou():
    assert mapear_status_pagamento(PaymentStatus.ERROR) == Transacao.Status.FALHOU


def test_mapear_status_pagamento_retorna_pendente_para_desconhecido():
    assert mapear_status_pagamento("unknown-status") == Transacao.Status.PENDENTE


def test_normalizar_uuid_com_string_valida():
    raw = str(uuid4())
    assert str(normalizar_uuid(raw)) == raw


def test_normalizar_uuid_com_valor_invalido():
    assert normalizar_uuid("invalido") is None

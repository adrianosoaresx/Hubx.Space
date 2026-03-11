from __future__ import annotations

from typing import Any
from uuid import UUID

from payments import PaymentStatus

from pagamentos.models import Transacao


def mapear_status_pagamento(status: str) -> str:
    if status == PaymentStatus.CONFIRMED:
        return Transacao.Status.APROVADA
    if status == PaymentStatus.REFUNDED:
        return Transacao.Status.ESTORNADA
    if status in {PaymentStatus.REJECTED, PaymentStatus.ERROR}:
        return Transacao.Status.FALHOU
    return Transacao.Status.PENDENTE


def normalizar_uuid(valor: Any) -> UUID | None:
    if isinstance(valor, UUID):
        return valor
    if valor is None:
        return None
    if isinstance(valor, str):
        valor = valor.strip()
        if not valor:
            return None
    try:
        return UUID(str(valor))
    except (TypeError, ValueError, AttributeError):
        return None

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from apps.backend.app.modules.pagamentos.domain.payment_return import normalize_return_status


class PaymentReturnLookupRepository(Protocol):
    def find_transaction(self, *, payment_token: str | None, payment_id: str | None): ...


@dataclass(frozen=True)
class PaymentReturnContext:
    status: str
    has_transaction: bool


class PaymentReturnUseCase:
    def __init__(self, *, lookup_repository: PaymentReturnLookupRepository) -> None:
        self._lookup_repository = lookup_repository

    def resolve_status(self, *, raw_status: str | None) -> str | None:
        return normalize_return_status(raw_status)

    def find_transaction(self, *, payment_token: str | None, payment_id: str | None):
        return self._lookup_repository.find_transaction(
            payment_token=payment_token,
            payment_id=payment_id,
        )

    @staticmethod
    def resolve_message(context: PaymentReturnContext) -> str:
        if not context.has_transaction:
            return "not_found"
        if context.status == "sucesso":
            return "success"
        if context.status == "falha":
            return "failure"
        return "pending"

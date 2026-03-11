import os
from types import SimpleNamespace

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.pagamentos.application.payment_return_flow import (  # noqa: E402
    PaymentReturnContext,
    PaymentReturnUseCase,
)


class _FakeLookupRepo:
    def __init__(self):
        self.called_with = None
        self.return_value = None

    def find_transaction(self, *, payment_token: str | None, payment_id: str | None):
        self.called_with = (payment_token, payment_id)
        return self.return_value


def test_payment_return_use_case_resolve_status():
    use_case = PaymentReturnUseCase(lookup_repository=_FakeLookupRepo())

    assert use_case.resolve_status(raw_status="Sucesso") == "sucesso"
    assert use_case.resolve_status(raw_status="desconhecido") is None


def test_payment_return_use_case_find_transaction_delegates():
    repo = _FakeLookupRepo()
    repo.return_value = SimpleNamespace(id=10)
    use_case = PaymentReturnUseCase(lookup_repository=repo)

    result = use_case.find_transaction(payment_token="tok", payment_id=None)

    assert result.id == 10
    assert repo.called_with == ("tok", None)


def test_payment_return_use_case_resolve_message():
    assert PaymentReturnUseCase.resolve_message(
        PaymentReturnContext(status="sucesso", has_transaction=False)
    ) == "not_found"
    assert PaymentReturnUseCase.resolve_message(
        PaymentReturnContext(status="sucesso", has_transaction=True)
    ) == "success"
    assert PaymentReturnUseCase.resolve_message(
        PaymentReturnContext(status="falha", has_transaction=True)
    ) == "failure"
    assert PaymentReturnUseCase.resolve_message(
        PaymentReturnContext(status="pendente", has_transaction=True)
    ) == "pending"

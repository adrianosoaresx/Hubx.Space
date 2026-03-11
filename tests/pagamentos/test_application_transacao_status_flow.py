import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.pagamentos.application.transacao_status_flow import (  # noqa: E402
    TransacaoStatusUseCase,
)


def test_transacao_status_decision_pending_requests_sync():
    use_case = TransacaoStatusUseCase()

    decision = use_case.decide(
        status="pending",
        has_inscricao=False,
        is_htmx_request=False,
    )

    assert decision.should_sync_payment_model is True
    assert decision.should_redirect_hx_to_inscricao is False
    assert decision.should_render_inscricao_result is False


def test_transacao_status_decision_approved_with_inscricao_htmx_redirects():
    use_case = TransacaoStatusUseCase()

    decision = use_case.decide(
        status="approved",
        has_inscricao=True,
        is_htmx_request=True,
    )

    assert decision.should_sync_payment_model is False
    assert decision.should_redirect_hx_to_inscricao is True
    assert decision.should_render_inscricao_result is False


def test_transacao_status_decision_approved_with_inscricao_renders_result():
    use_case = TransacaoStatusUseCase()

    decision = use_case.decide(
        status="approved",
        has_inscricao=True,
        is_htmx_request=False,
    )

    assert decision.should_sync_payment_model is False
    assert decision.should_redirect_hx_to_inscricao is False
    assert decision.should_render_inscricao_result is True

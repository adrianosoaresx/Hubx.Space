import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.pagamentos.interfaces.http_responses import (  # noqa: E402
    build_hx_redirect_response,
    build_invalid_return_status_response,
    build_invalid_transaction_response,
    build_payment_return_message,
    build_webhook_invalid_signature_response,
    build_webhook_missing_external_id_response,
    build_webhook_processed_response,
)


def test_build_invalid_transaction_response():
    response = build_invalid_transaction_response()
    assert response.status_code == 400
    assert response.content == b"invalid transaction"


def test_build_hx_redirect_response_sets_header():
    response = build_hx_redirect_response(redirect_url="/eventos/resultado/")
    assert response.status_code == 204
    assert response["HX-Redirect"] == "/eventos/resultado/"


def test_build_invalid_return_status_response():
    response = build_invalid_return_status_response()
    assert response.status_code == 400
    assert response.content == b"invalid status"


def test_build_payment_return_message_variants():
    assert "Não localizamos a transação" in build_payment_return_message(message_key="not_found")
    assert "Pagamento confirmado" in build_payment_return_message(message_key="success")
    assert "não foi concluído" in build_payment_return_message(message_key="failure")
    assert "Pagamento em análise" in build_payment_return_message(message_key="pending")


def test_build_webhook_error_and_processed_responses():
    assert build_webhook_missing_external_id_response().status_code == 400
    assert build_webhook_invalid_signature_response().status_code == 403
    assert build_webhook_processed_response(http_status=200).status_code == 200

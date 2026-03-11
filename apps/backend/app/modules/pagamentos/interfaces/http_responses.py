from __future__ import annotations

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.utils.translation import gettext as _


def build_invalid_transaction_response() -> HttpResponseBadRequest:
    return HttpResponseBadRequest("invalid transaction")


def build_hx_redirect_response(*, redirect_url: str) -> HttpResponse:
    response = HttpResponse(status=204)
    response["HX-Redirect"] = redirect_url
    return response


def build_invalid_return_status_response() -> HttpResponseBadRequest:
    return HttpResponseBadRequest("invalid status")


def build_payment_return_message(*, message_key: str) -> str:
    if message_key == "not_found":
        return _("Não localizamos a transação informada. Verifique os dados ou tente novamente.")
    if message_key == "success":
        return _("Pagamento confirmado. Estamos validando seus dados.")
    if message_key == "failure":
        return _("Pagamento não foi concluído. Você pode tentar novamente ou escolher outro método.")
    return _("Pagamento em análise. Assim que houver atualização, atualizaremos este status.")


def build_webhook_missing_external_id_response() -> HttpResponseBadRequest:
    return HttpResponseBadRequest("missing id")


def build_webhook_invalid_signature_response() -> HttpResponseForbidden:
    return HttpResponseForbidden()


def build_webhook_processed_response(*, http_status: int) -> HttpResponse:
    return HttpResponse(status=http_status)

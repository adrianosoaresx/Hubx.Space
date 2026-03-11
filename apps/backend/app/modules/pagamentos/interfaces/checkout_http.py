from __future__ import annotations

from django.urls import reverse


def checkout_form_error_status() -> int:
    return 400


def build_pix_checkout_context(*, form, provider_public_key: str | None) -> dict:
    return {
        "form": form,
        "provider_public_key": provider_public_key,
    }


def build_checkout_result_redirect_url(*, transacao_pk: int) -> str:
    return reverse(
        "pagamentos:checkout-resultado",
        kwargs={"pk": transacao_pk},
    )


def build_faturamento_checkout_context(*, form) -> dict:
    return {"form": form}

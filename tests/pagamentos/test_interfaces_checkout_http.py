import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.pagamentos.interfaces.checkout_http import (  # noqa: E402
    build_checkout_result_redirect_url,
    build_faturamento_checkout_context,
    build_pix_checkout_context,
    checkout_form_error_status,
)


def test_checkout_form_error_status_is_400():
    assert checkout_form_error_status() == 400


def test_build_pix_checkout_context_contains_form_and_provider_key():
    context = build_pix_checkout_context(form="form_obj", provider_public_key="pk_test")
    assert context["form"] == "form_obj"
    assert context["provider_public_key"] == "pk_test"


def test_build_faturamento_checkout_context_contains_form():
    context = build_faturamento_checkout_context(form="form_obj")
    assert context == {"form": "form_obj"}


def test_build_checkout_result_redirect_url_points_to_checkout_result():
    url = build_checkout_result_redirect_url(transacao_pk=123)
    assert url.endswith("/pagamentos/checkout/resultado/123/")

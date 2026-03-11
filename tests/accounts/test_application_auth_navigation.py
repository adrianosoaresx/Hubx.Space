import os

import django
from django.test import RequestFactory

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.accounts.application.auth_navigation import (  # noqa: E402
    get_validated_redirect_url,
)


def test_get_validated_redirect_url_accepts_internal_path():
    request = RequestFactory().post("/accounts/login/", {"next": "/eventos/"}, HTTP_HOST="testserver")
    assert get_validated_redirect_url(request, fallback_url="/accounts/perfil/") == "/eventos/"


def test_get_validated_redirect_url_rejects_external_url():
    request = RequestFactory().post(
        "/accounts/login/",
        {"next": "https://evil.example.com/pwn"},
        HTTP_HOST="testserver",
    )
    assert get_validated_redirect_url(request, fallback_url="/accounts/perfil/") == "/accounts/perfil/"

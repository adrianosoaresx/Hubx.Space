from __future__ import annotations

import os

import django
import pytest
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from accounts.models import UserType
from audit.middleware import AuditMiddleware
from organizacoes.models import Organizacao

User = get_user_model()


def _create_user(username: str):
    org = Organizacao.objects.create(
        nome=f"Org {username}",
        cnpj=f"33445566{Organizacao.objects.count() + 1000:04d}95",
    )
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="senha123",
        user_type=UserType.NUCLEADO,
        organizacao=org,
    )


@pytest.mark.django_db
def test_audit_middleware_loga_request_membros(monkeypatch):
    captured: dict = {}

    async def fake_log_audit_async(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr("audit.middleware.log_audit_async", fake_log_audit_async)
    monkeypatch.setattr("audit.middleware.hash_ip", lambda ip: f"hash:{ip}")
    monkeypatch.setattr("audit.middleware.get_client_ip", lambda request: "127.0.0.1")

    middleware = AuditMiddleware(lambda request: HttpResponse(status=404))
    request = RequestFactory().get("/membros/inexistente/", {"token": "secret", "q": "ok"})
    request.user = _create_user("audit_mw_user")

    response = middleware(request)

    assert response.status_code == 404
    assert captured["action"] == "GET:/membros/inexistente/"
    assert captured["status"] == "FAILURE"
    assert captured["metadata"] == {"token": "secret", "q": "ok"}
    assert captured["ip_hash"] == "hash:127.0.0.1"

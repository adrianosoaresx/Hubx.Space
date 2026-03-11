from __future__ import annotations

import os

import django
import pytest
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from accounts.models import UserType
from audit.models import AuditLog
from audit.services import log_audit
from organizacoes.models import Organizacao

User = get_user_model()


def _create_user(username: str):
    org = Organizacao.objects.create(
        nome=f"Org {username}",
        cnpj=f"22334455{Organizacao.objects.count() + 1000:04d}95",
    )
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="senha123",
        user_type=UserType.NUCLEADO,
        organizacao=org,
    )


@pytest.mark.django_db
def test_log_audit_normaliza_status_e_sanitiza_metadata():
    user = _create_user("audit_user")

    log_audit(
        user=user,
        action="GET:/membros/",
        status="error",
        ip_hash="hash",
        metadata={"token": "secret", "query": "ok"},
    )

    log = AuditLog.objects.first()
    assert log is not None
    assert log.status == AuditLog.Status.FAILURE
    assert log.metadata["query"] == "ok"
    assert "token" not in log.metadata
    assert log.metadata["severity"] == "high"

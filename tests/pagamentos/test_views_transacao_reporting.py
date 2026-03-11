import os
from decimal import Decimal

import django
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from organizacoes.models import Organizacao  # noqa: E402
from pagamentos.models import Pedido, Transacao  # noqa: E402


def _create_admin_client():
    user_model = get_user_model()
    admin_user = user_model.objects.create_user(
        username="admin.revisao",
        email="admin.revisao@example.com",
        password="senha123forte",
        is_staff=True,
    )
    client = Client()
    client.force_login(admin_user)
    return client


@pytest.mark.django_db
def test_transacao_revisao_filters_failed_only():
    organizacao = Organizacao.objects.create(nome="Org Revisao", cnpj="12345678000198")
    pedido = Pedido.objects.create(
        organizacao=organizacao,
        valor=Decimal("100.00"),
        status=Pedido.Status.PENDENTE,
    )
    Transacao.objects.create(
        pedido=pedido,
        metodo=Transacao.Metodo.PIX,
        valor=Decimal("100.00"),
        status=Transacao.Status.PENDENTE,
        external_id="rev-pending",
    )
    failed_tx = Transacao.objects.create(
        pedido=pedido,
        metodo=Transacao.Metodo.PIX,
        valor=Decimal("100.00"),
        status=Transacao.Status.FALHOU,
        external_id="rev-failed",
    )
    client = _create_admin_client()

    response = client.get(reverse("pagamentos:relatorios") + "?status=failed")

    assert response.status_code == 200
    transacoes = list(response.context["transacoes"])
    assert len(transacoes) == 1
    assert transacoes[0].id == failed_tx.id


@pytest.mark.django_db
def test_transacao_csv_export_returns_csv_content():
    organizacao = Organizacao.objects.create(nome="Org CSV", cnpj="12345678000199")
    pedido = Pedido.objects.create(
        organizacao=organizacao,
        valor=Decimal("80.00"),
        status=Pedido.Status.PENDENTE,
    )
    Transacao.objects.create(
        pedido=pedido,
        metodo=Transacao.Metodo.PIX,
        valor=Decimal("80.00"),
        status=Transacao.Status.PENDENTE,
        external_id="csv-tx-1",
    )
    client = _create_admin_client()

    response = client.get(reverse("pagamentos:transacoes-csv"))

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/csv")
    content = response.content.decode("utf-8")
    assert "data,valor,status,metodo" in content
    assert ",80.00,pending,pix" in content

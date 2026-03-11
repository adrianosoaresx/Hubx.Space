import os
from datetime import timedelta
from decimal import Decimal

import django
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from eventos.models import Evento, InscricaoEvento  # noqa: E402
from organizacoes.models import Organizacao  # noqa: E402
from pagamentos.models import Pedido, Transacao  # noqa: E402


@pytest.mark.django_db
def test_transacao_status_invalid_transaction_returns_400():
    client = Client()

    response = client.get(reverse("pagamentos:status", kwargs={"pk": 999999}))

    assert response.status_code == 400


@pytest.mark.django_db
def test_transacao_status_approved_with_inscricao_htmx_redirects():
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="status.user",
        email="status@example.com",
        password="senha123forte",
    )
    organizacao = Organizacao.objects.create(nome="Org Status", cnpj="12345678000197")
    evento = Evento.objects.create(
        titulo="Evento Status",
        slug="evento-status",
        descricao="Descricao",
        data_inicio=timezone.now() + timedelta(days=2),
        data_fim=timezone.now() + timedelta(days=3),
        local="Local",
        cidade="Cidade",
        estado="SP",
        cep="12345-678",
        organizacao=organizacao,
        status=Evento.Status.ATIVO,
        publico_alvo=0,
        gratuito=False,
        valor_associado=Decimal("120.00"),
        valor_nucleado=Decimal("120.00"),
    )
    pedido = Pedido.objects.create(
        organizacao=organizacao,
        valor=Decimal("120.00"),
        status=Pedido.Status.PAGO,
        email=user.email,
        nome="Usuario",
    )
    transacao = Transacao.objects.create(
        pedido=pedido,
        metodo=Transacao.Metodo.PIX,
        valor=Decimal("120.00"),
        status=Transacao.Status.APROVADA,
        external_id="status-approved-001",
    )
    inscricao = InscricaoEvento.objects.create(
        user=user,
        evento=evento,
        transacao=transacao,
        metodo_pagamento=Transacao.Metodo.PIX,
        pagamento_validado=True,
        valor_pago=Decimal("120.00"),
    )

    client = Client()
    response = client.get(
        reverse("pagamentos:status", kwargs={"pk": transacao.pk}),
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 204
    assert response.headers["HX-Redirect"] == reverse(
        "eventos:inscricao_resultado",
        kwargs={"uuid": inscricao.uuid},
    )

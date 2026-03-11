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

from accounts.models import UserType  # noqa: E402
from eventos.models import Evento, InscricaoEvento  # noqa: E402
from organizacoes.models import Organizacao  # noqa: E402
from pagamentos.models import Pedido, Transacao  # noqa: E402

User = get_user_model()


def _create_organizacao() -> Organizacao:
    return Organizacao.objects.create(nome="Org Int EP", cnpj="12345678000992")


def _create_usuario(organizacao: Organizacao) -> User:
    return User.objects.create_user(
        username="integracao.ep.user",
        email="integracao.ep.user@example.com",
        password="senha123forte",
        user_type=UserType.ASSOCIADO,
        organizacao=organizacao,
    )


def _create_evento_pago(organizacao: Organizacao) -> Evento:
    inicio = timezone.now() + timedelta(days=2)
    return Evento.objects.create(
        titulo="Evento Integracao EP",
        slug=f"evento-integracao-ep-{int(timezone.now().timestamp())}",
        descricao="Descricao",
        data_inicio=inicio,
        data_fim=inicio + timedelta(hours=3),
        local="Local",
        cidade="Cidade",
        estado="SP",
        cep="12345-678",
        organizacao=organizacao,
        status=Evento.Status.ATIVO,
        publico_alvo=0,
        gratuito=False,
        valor_associado=Decimal("150.00"),
        valor_nucleado=Decimal("150.00"),
    )


@pytest.mark.django_db
def test_integracao_eventos_pagamentos_status_resultado():
    organizacao = _create_organizacao()
    usuario = _create_usuario(organizacao)
    evento = _create_evento_pago(organizacao)

    client = Client()
    client.force_login(usuario)

    create_response = client.post(
        reverse("eventos:inscricao_criar", kwargs={"pk": evento.pk}),
        data={"metodo_pagamento": "pix"},
    )
    assert create_response.status_code == 302

    inscricao = InscricaoEvento.all_objects.get(user=usuario, evento=evento)
    assert inscricao.status == "pendente"

    pedido = Pedido.objects.create(
        organizacao=organizacao,
        valor=Decimal("150.00"),
        status=Pedido.Status.PAGO,
        email=usuario.email,
        nome=usuario.get_full_name(),
    )
    transacao = Transacao.objects.create(
        pedido=pedido,
        metodo=Transacao.Metodo.PIX,
        valor=Decimal("150.00"),
        status=Transacao.Status.APROVADA,
        external_id="integracao-ep-001",
    )

    inscricao.transacao = transacao
    inscricao.metodo_pagamento = Transacao.Metodo.PIX
    inscricao.pagamento_validado = True
    inscricao.valor_pago = Decimal("150.00")
    inscricao.save(
        update_fields=["transacao", "metodo_pagamento", "pagamento_validado", "valor_pago"]
    )

    status_response = client.get(
        reverse("pagamentos:status", kwargs={"pk": transacao.pk}),
        HTTP_HX_REQUEST="true",
    )
    assert status_response.status_code == 204

    expected_result_url = reverse("eventos:inscricao_resultado", kwargs={"uuid": inscricao.uuid})
    assert status_response.headers["HX-Redirect"] == expected_result_url

    resultado_response = client.get(expected_result_url)
    assert resultado_response.status_code == 200

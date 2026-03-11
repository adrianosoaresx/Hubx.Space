import os

import django
import pytest
from django.test import Client
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()


@pytest.mark.django_db
def test_mercadopago_retorno_status_invalido():
    client = Client()

    response = client.get(
        reverse("pagamentos:mercadopago-retorno", kwargs={"status": "invalido"})
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_mercadopago_retorno_sem_transacao_exibe_mensagem():
    client = Client()

    response = client.get(
        reverse("pagamentos:mercadopago-retorno", kwargs={"status": "sucesso"})
    )

    assert response.status_code == 200
    assert b"N\xc3\xa3o localizamos a transa\xc3\xa7\xc3\xa3o informada" in response.content


@pytest.mark.django_db
def test_mercadopago_retorno_com_token_inexistente_exibe_mensagem_not_found():
    client = Client()

    response = client.get(
        reverse("pagamentos:mercadopago-retorno", kwargs={"status": "sucesso"}),
        data={"token": "token-inexistente-123"},
    )

    assert response.status_code == 200
    assert b"N\xc3\xa3o localizamos a transa\xc3\xa7\xc3\xa3o informada" in response.content

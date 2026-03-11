import os

import django
import pytest
from django.test import Client
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from accounts.factories import UserFactory  # noqa: E402
from nucleos.factories import NucleoFactory  # noqa: E402
from organizacoes.factories import OrganizacaoFactory  # noqa: E402


@pytest.mark.django_db
def test_perfil_info_get_sem_htmx_redireciona_para_secao_edit():
    organizacao = OrganizacaoFactory()
    nucleo = NucleoFactory(organizacao=organizacao)
    user = UserFactory(
        user_type="admin",
        organizacao=organizacao,
        nucleo_obj=nucleo,
    )
    client = Client()
    client.force_login(user)

    response = client.get(reverse("accounts:perfil_sections_info"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("accounts:perfil"))
    assert "section=info" in response.url
    assert "info_view=edit" in response.url


@pytest.mark.django_db
def test_perfil_info_get_htmx_renderiza_formulario():
    organizacao = OrganizacaoFactory()
    nucleo = NucleoFactory(organizacao=organizacao)
    user = UserFactory(
        user_type="admin",
        organizacao=organizacao,
        nucleo_obj=nucleo,
    )
    client = Client()
    client.force_login(user)

    response = client.get(
        reverse("accounts:perfil_sections_info"),
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 200
    assert b"perfil-info-form" in response.content


@pytest.mark.django_db
def test_perfil_info_post_htmx_success_retornando_hx_redirect():
    organizacao = OrganizacaoFactory()
    nucleo = NucleoFactory(organizacao=organizacao)
    user = UserFactory(
        user_type="admin",
        organizacao=organizacao,
        nucleo_obj=nucleo,
        cpf="390.533.447-05",
    )
    client = Client()
    client.force_login(user)

    response = client.post(
        reverse("accounts:perfil_sections_info"),
        {
            "username": user.username,
            "contato": "Contato Atualizado",
            "email": user.email,
            "cpf": "390.533.447-05",
            "cnpj": "",
            "razao_social": "",
            "nome_fantasia": "",
            "area_atuacao": "",
            "descricao_atividade": "",
            "phone_number": "",
            "whatsapp": "",
            "birth_date": "",
            "endereco": "",
            "cidade": "",
            "estado": "",
            "cep": "",
            "facebook": "",
            "twitter": "",
            "instagram": "",
            "linkedin": "",
            "biografia": "",
        },
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 204
    assert "HX-Redirect" in response.headers
    assert "section=info" in response.headers["HX-Redirect"]

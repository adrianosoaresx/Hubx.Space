import os
from types import SimpleNamespace

import django
from django.test import RequestFactory, override_settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.pagamentos.application.organization_resolution import (
    obter_organizacao_checkout,
    obter_organizacao_webhook,
)
from organizacoes.models import Organizacao


def _upsert_org(cnpj: str, **defaults) -> Organizacao:
    org = Organizacao.objects.filter(cnpj=cnpj).first()
    if org is None:
        return Organizacao.objects.create(cnpj=cnpj, **defaults)
    for field, value in defaults.items():
        setattr(org, field, value)
    org.save(update_fields=[*defaults.keys(), "updated_at"])
    return org


def test_obter_organizacao_checkout_por_id_no_querystring():
    org = _upsert_org(nome="Org Query", cnpj="12345678000195")
    request = RequestFactory().get("/pagamentos/checkout/pix/", {"organizacao_id": str(org.id)})

    result = obter_organizacao_checkout(request)

    assert result == org


@override_settings(ALLOWED_HOSTS=["orghost.hubx.local", "testserver", "localhost"])
def test_obter_organizacao_checkout_por_host_nome_site():
    org = _upsert_org(
        nome="Org Host",
        cnpj="98765432000195",
        nome_site="orghost",
    )
    request = RequestFactory().get("/pagamentos/checkout/pix/", HTTP_HOST="orghost.hubx.local")

    result = obter_organizacao_checkout(request)

    assert result == org


def test_obter_organizacao_webhook_prioriza_org_da_transacao():
    org = _upsert_org(nome="Org Transacao", cnpj="11223344000195")
    request = RequestFactory().post("/pagamentos/webhook/", HTTP_HOST="outro.hubx.local")
    transacao = SimpleNamespace(pedido=SimpleNamespace(organizacao_id=org.id, organizacao=org))

    result = obter_organizacao_webhook(request, _payload={}, transacao=transacao)

    assert result == org

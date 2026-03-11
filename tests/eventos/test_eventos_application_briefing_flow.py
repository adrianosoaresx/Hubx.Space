import os
from datetime import timedelta

import django
import pytest
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.eventos.application.briefing_flow import (
    apply_briefing_template_selection,
    build_briefing_select_initial,
    get_evento_briefing,
)
from eventos.models import BriefingEvento, BriefingTemplate, Evento
from organizacoes.models import Organizacao


def _create_org() -> Organizacao:
    return Organizacao.objects.create(nome="Org Briefing App", cnpj="72345678000195")


def _create_evento(org: Organizacao, slug: str) -> Evento:
    inicio = timezone.now() + timedelta(days=2)
    return Evento.objects.create(
        titulo="Evento Briefing",
        slug=slug,
        descricao="Descricao",
        data_inicio=inicio,
        data_fim=inicio + timedelta(hours=2),
        local="Local",
        cidade="Cidade",
        estado="SP",
        cep="12345-678",
        organizacao=org,
        status=Evento.Status.ATIVO,
        publico_alvo=0,
        gratuito=True,
    )


@pytest.mark.django_db
def test_build_briefing_select_initial_when_unbound_and_has_briefing():
    org = _create_org()
    evento = _create_evento(org, "evt-brief-init")
    template = BriefingTemplate.objects.create(nome="T1", estrutura=[])
    BriefingEvento.objects.create(evento=evento, template=template)

    initial = build_briefing_select_initial(evento, form_is_bound=False)

    assert initial == {"template": template.id}


@pytest.mark.django_db
def test_apply_briefing_template_selection_creates_briefing():
    org = _create_org()
    evento = _create_evento(org, "evt-brief-create")
    template = BriefingTemplate.objects.create(nome="T1", estrutura=[])

    briefing = apply_briefing_template_selection(evento, template)

    assert briefing.evento_id == evento.id
    assert briefing.template_id == template.id


@pytest.mark.django_db
def test_apply_briefing_template_selection_resets_respostas_on_template_change():
    org = _create_org()
    evento = _create_evento(org, "evt-brief-update")
    template_a = BriefingTemplate.objects.create(nome="TA", estrutura=[])
    template_b = BriefingTemplate.objects.create(nome="TB", estrutura=[])
    briefing = BriefingEvento.objects.create(
        evento=evento,
        template=template_a,
        respostas={"Campo": "Valor"},
    )

    updated = apply_briefing_template_selection(evento, template_b)

    briefing.refresh_from_db()
    assert updated.id == briefing.id
    assert briefing.template_id == template_b.id
    assert briefing.respostas == {}


@pytest.mark.django_db
def test_get_evento_briefing_returns_related():
    org = _create_org()
    evento = _create_evento(org, "evt-brief-get")
    template = BriefingTemplate.objects.create(nome="TC", estrutura=[])
    briefing = BriefingEvento.objects.create(evento=evento, template=template)

    assert get_evento_briefing(evento) == briefing

from __future__ import annotations

import json
import os

import django
import pytest
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from accounts.models import UserType
from apps.backend.app.modules.membros.application.promotion_form_context import (
    build_promocao_form_context,
)
from nucleos.models import Nucleo, ParticipacaoNucleo
from organizacoes.models import Organizacao

User = get_user_model()


def _create_org() -> Organizacao:
    return Organizacao.objects.create(
        nome=f"Org Context {Organizacao.objects.count()}",
        cnpj=f"22110033{Organizacao.objects.count() + 1000:04d}95",
    )


def _create_user(org: Organizacao, username: str, user_type: UserType):
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="senha123",
        user_type=user_type,
        organizacao=org,
    )


@pytest.mark.django_db
def test_build_promocao_form_context_retorna_flags_e_mensagens_indisponiveis():
    org = _create_org()
    membro = _create_user(org, "context_membro_1", UserType.NUCLEADO)
    outro = _create_user(org, "context_outro_1", UserType.NUCLEADO)
    nucleo = Nucleo.objects.create(organizacao=org, nome="N Context A", consultor=membro)

    ParticipacaoNucleo.objects.create(
        user=membro,
        nucleo=nucleo,
        papel="membro",
        status="ativo",
    )
    ParticipacaoNucleo.objects.create(
        user=outro,
        nucleo=nucleo,
        papel="coordenador",
        papel_coordenador=ParticipacaoNucleo.PapelCoordenador.COORDENADOR_GERAL,
        status="ativo",
    )

    context = build_promocao_form_context(
        membro=membro,
        organizacao=org,
        selected_nucleado=[nucleo.id],
        selected_coordenador_roles={nucleo.id: "coordenador_geral"},
        form_errors=["erro x"],
        success_message="ok",
        origin_section="nucleado",
    )

    assert context["membro"] == membro
    assert context["is_guest"] is False
    assert context["selected_nucleado"] == [str(nucleo.id)]
    assert context["selected_coordenador_roles"] == {str(nucleo.id): "coordenador_geral"}
    assert context["form_errors"] == ["erro x"]
    assert context["success_message"] == "ok"
    assert context["origin_section"] == "nucleado"
    assert ParticipacaoNucleo.PapelCoordenador.COORDENADOR_GERAL in context["restricted_roles"]

    assert len(context["nucleos"]) == 1
    nucleo_ctx = context["nucleos"][0]
    assert nucleo_ctx["id"] == str(nucleo.id)
    assert nucleo_ctx["is_current_member"] is True
    assert nucleo_ctx["is_current_consultor"] is True
    assert (
        ParticipacaoNucleo.PapelCoordenador.COORDENADOR_GERAL
        in nucleo_ctx["unavailable_roles"]
    )
    unavailable_messages = json.loads(nucleo_ctx["unavailable_messages_json"])
    assert ParticipacaoNucleo.PapelCoordenador.COORDENADOR_GERAL in unavailable_messages
    assert outro.username in unavailable_messages[
        ParticipacaoNucleo.PapelCoordenador.COORDENADOR_GERAL
    ]


@pytest.mark.django_db
def test_build_promocao_form_context_mapeia_roles_do_usuario():
    org = _create_org()
    membro = _create_user(org, "context_membro_2", UserType.COORDENADOR)
    nucleo_a = Nucleo.objects.create(organizacao=org, nome="N Context A")
    nucleo_b = Nucleo.objects.create(organizacao=org, nome="N Context B")

    ParticipacaoNucleo.objects.create(
        user=membro,
        nucleo=nucleo_b,
        papel="coordenador",
        papel_coordenador=ParticipacaoNucleo.PapelCoordenador.VICE_COORDENADOR,
        status="ativo",
    )

    context = build_promocao_form_context(
        membro=membro,
        organizacao=org,
    )

    role_map = json.loads(context["user_role_map_json"])
    assert role_map[ParticipacaoNucleo.PapelCoordenador.VICE_COORDENADOR] == [
        str(nucleo_b.id)
    ]

    nucleo_b_ctx = next(item for item in context["nucleos"] if item["id"] == str(nucleo_b.id))
    assert nucleo_b_ctx["is_current_coordinator"] is True
    assert ParticipacaoNucleo.PapelCoordenador.VICE_COORDENADOR in nucleo_b_ctx[
        "user_current_roles"
    ]

    nucleo_a_ctx = next(item for item in context["nucleos"] if item["id"] == str(nucleo_a.id))
    assert nucleo_a_ctx["is_current_coordinator"] is False

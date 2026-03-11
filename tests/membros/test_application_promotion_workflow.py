from __future__ import annotations

import os

import django
import pytest
from django.contrib.auth import get_user_model
from django.http import QueryDict

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from accounts.models import UserType
from apps.backend.app.modules.membros.application.promotion_workflow import (
    build_promocao_input,
    execute_promocao_from_post,
    execute_promocao_workflow,
)
from nucleos.models import Nucleo, ParticipacaoNucleo
from organizacoes.models import Organizacao

User = get_user_model()


def _create_org() -> Organizacao:
    return Organizacao.objects.create(
        nome=f"Org Workflow {Organizacao.objects.count()}",
        cnpj=f"33112244{Organizacao.objects.count() + 1000:04d}95",
    )


def _create_user(org: Organizacao, username: str, user_type: UserType):
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="senha123",
        user_type=user_type,
        organizacao=org,
    )


def _new_post() -> QueryDict:
    return QueryDict("", mutable=True)


@pytest.mark.django_db
def test_execute_promocao_from_post_retorna_erro_para_coordenacao_sem_papel():
    org = _create_org()
    membro = _create_user(org, "workflow_membro_1", UserType.NUCLEADO)
    nucleo = Nucleo.objects.create(organizacao=org, nome="N Workflow 1")

    post = _new_post()
    post.setlist("coordenador_nucleos", [str(nucleo.id)])

    result = execute_promocao_from_post(
        membro=membro,
        organizacao=org,
        post_data=post,
    )

    assert result.success is False
    assert any("papel de coordenação" in str(err) for err in result.form_errors)
    assert result.selected_coordenador == [str(nucleo.id)]


@pytest.mark.django_db
def test_execute_promocao_from_post_aplica_promocao_nucleado_e_sync_estado():
    org = _create_org()
    membro = _create_user(org, "workflow_membro_2", UserType.CONVIDADO)
    nucleo = Nucleo.objects.create(organizacao=org, nome="N Workflow 2")

    post = _new_post()
    post.setlist("nucleado_nucleos", [str(nucleo.id)])
    post["promover_associado"] = "1"

    result = execute_promocao_from_post(
        membro=membro,
        organizacao=org,
        post_data=post,
    )

    membro.refresh_from_db()
    participacao = ParticipacaoNucleo.objects.get(user=membro, nucleo=nucleo)

    assert result.success is True
    assert result.form_errors == []
    assert membro.user_type == UserType.NUCLEADO.value
    assert membro.is_associado is True
    assert participacao.status == "ativo"
    assert participacao.papel == "membro"


@pytest.mark.django_db
def test_execute_promocao_workflow_com_dto_sem_querydict():
    org = _create_org()
    membro = _create_user(org, "workflow_membro_3", UserType.CONVIDADO)
    nucleo = Nucleo.objects.create(organizacao=org, nome="N Workflow 3")

    workflow_input = build_promocao_input(
        current_user_type=membro.user_type,
        raw_nucleado=[str(nucleo.id)],
        raw_consultor=[],
        raw_coordenador=[],
        raw_remover_nucleado=[],
        raw_remover_consultor=[],
        raw_remover_coordenador=[],
        role_values_by_nucleo={},
        raw_promover_associado="1",
    )
    result = execute_promocao_workflow(
        membro=membro,
        organizacao=org,
        workflow_input=workflow_input,
    )

    membro.refresh_from_db()
    participacao = ParticipacaoNucleo.objects.get(user=membro, nucleo=nucleo)

    assert result.success is True
    assert membro.user_type == UserType.NUCLEADO.value
    assert membro.is_associado is True
    assert participacao.status == "ativo"

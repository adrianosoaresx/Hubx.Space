from __future__ import annotations

import os

import django
import pytest
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from accounts.models import UserType
from apps.backend.app.modules.membros.application.promotion_persistence import (
    apply_promocao_persistence,
)
from nucleos.models import Nucleo, ParticipacaoNucleo
from organizacoes.models import Organizacao

User = get_user_model()


def _create_org() -> Organizacao:
    return Organizacao.objects.create(
        nome=f"Org Persist {Organizacao.objects.count()}",
        cnpj=f"88990011{Organizacao.objects.count() + 1000:04d}95",
    )


def _create_user(org: Organizacao, username: str):
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="senha123",
        user_type=UserType.NUCLEADO,
        organizacao=org,
    )


@pytest.mark.django_db
def test_apply_promocao_persistence_define_consultor_e_coordenador():
    org = _create_org()
    membro = _create_user(org, "persist_membro_1")
    nucleo = Nucleo.objects.create(organizacao=org, nome="N Persist 1")
    participacao = ParticipacaoNucleo.objects.create(
        user=membro,
        nucleo=nucleo,
        papel="membro",
        status="inativo",
        status_suspensao=True,
    )

    apply_promocao_persistence(
        membro=membro,
        organizacao=org,
        valid_action_ids={nucleo.id},
        valid_ids={nucleo.id},
        valid_consultor_ids={nucleo.id},
        nucleado_ids=[],
        coordenador_roles={
            nucleo.id: ParticipacaoNucleo.PapelCoordenador.COORDENADOR_GERAL
        },
        remover_nucleado_ids=[],
        remover_consultor_ids=[],
        remover_coordenador_ids=[],
    )

    nucleo.refresh_from_db()
    participacao.refresh_from_db()

    assert nucleo.consultor_id == membro.id
    assert participacao.status == "ativo"
    assert participacao.status_suspensao is False
    assert participacao.papel == "coordenador"
    assert (
        participacao.papel_coordenador
        == ParticipacaoNucleo.PapelCoordenador.COORDENADOR_GERAL
    )


@pytest.mark.django_db
def test_apply_promocao_persistence_cria_participacao_para_nucleado():
    org = _create_org()
    membro = _create_user(org, "persist_membro_2")
    nucleo = Nucleo.objects.create(organizacao=org, nome="N Persist 2")

    apply_promocao_persistence(
        membro=membro,
        organizacao=org,
        valid_action_ids={nucleo.id},
        valid_ids={nucleo.id},
        valid_consultor_ids=set(),
        nucleado_ids=[nucleo.id],
        coordenador_roles={},
        remover_nucleado_ids=[],
        remover_consultor_ids=[],
        remover_coordenador_ids=[],
    )

    participacao = ParticipacaoNucleo.objects.get(user=membro, nucleo=nucleo)
    assert participacao.status == "ativo"
    assert participacao.papel == "membro"
    assert participacao.papel_coordenador in (None, "")


@pytest.mark.django_db
def test_apply_promocao_persistence_remove_consultor_coordenador_e_nucleado():
    org = _create_org()
    membro = _create_user(org, "persist_membro_3")
    nucleo = Nucleo.objects.create(organizacao=org, nome="N Persist 3", consultor=membro)
    participacao = ParticipacaoNucleo.objects.create(
        user=membro,
        nucleo=nucleo,
        papel="coordenador",
        papel_coordenador=ParticipacaoNucleo.PapelCoordenador.COORDENADOR_GERAL,
        status="ativo",
    )

    apply_promocao_persistence(
        membro=membro,
        organizacao=org,
        valid_action_ids={nucleo.id},
        valid_ids=set(),
        valid_consultor_ids=set(),
        nucleado_ids=[],
        coordenador_roles={},
        remover_nucleado_ids=[nucleo.id],
        remover_consultor_ids=[nucleo.id],
        remover_coordenador_ids=[nucleo.id],
    )

    nucleo.refresh_from_db()
    participacao.refresh_from_db()

    assert nucleo.consultor_id is None
    assert participacao.status == "inativo"
    assert participacao.papel == "membro"
    assert participacao.papel_coordenador in (None, "")
    assert participacao.status_suspensao is False

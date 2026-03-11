from __future__ import annotations

import os

import django
import pytest
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from accounts.models import UserType
from apps.backend.app.modules.membros.application.promotion_conflicts import (
    validate_promocao_conflicts,
)
from nucleos.models import Nucleo, ParticipacaoNucleo
from organizacoes.models import Organizacao

User = get_user_model()


def _create_org() -> Organizacao:
    return Organizacao.objects.create(
        nome=f"Org Membros {Organizacao.objects.count()}",
        cnpj=f"77889900{Organizacao.objects.count() + 1000:04d}95",
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
def test_validate_promocao_conflicts_exige_papel_para_coordenador():
    org = _create_org()
    membro = _create_user(org, "membro_1")
    nucleo = Nucleo.objects.create(organizacao=org, nome="N1")

    errors, _ = validate_promocao_conflicts(
        membro=membro,
        coordenador_ids=[nucleo.id],
        coordenador_roles={},
        valid_action_ids={nucleo.id},
        nucleado_ids=[],
        consultor_ids=[],
        remover_nucleado_ids=[],
        remover_consultor_ids=[],
        remover_coordenador_ids=[],
    )

    assert any("papel de coordenação" in str(err) for err in errors)


@pytest.mark.django_db
def test_validate_promocao_conflicts_bloqueia_sobreposicao_consultor_coordenador():
    org = _create_org()
    membro = _create_user(org, "membro_2")
    nucleo = Nucleo.objects.create(organizacao=org, nome="N2")

    errors, _ = validate_promocao_conflicts(
        membro=membro,
        coordenador_ids=[nucleo.id],
        coordenador_roles={
            nucleo.id: ParticipacaoNucleo.PapelCoordenador.COORDENADOR_GERAL
        },
        valid_action_ids={nucleo.id},
        nucleado_ids=[],
        consultor_ids=[nucleo.id],
        remover_nucleado_ids=[],
        remover_consultor_ids=[],
        remover_coordenador_ids=[],
    )

    assert any("uma opção de promoção" in str(err) for err in errors)


@pytest.mark.django_db
def test_validate_promocao_conflicts_detecta_consultor_ocupado():
    org = _create_org()
    membro = _create_user(org, "membro_3")
    outro_consultor = _create_user(org, "consultor_ocupado")
    nucleo = Nucleo.objects.create(organizacao=org, nome="N3", consultor=outro_consultor)

    errors, _ = validate_promocao_conflicts(
        membro=membro,
        coordenador_ids=[],
        coordenador_roles={},
        valid_action_ids={nucleo.id},
        nucleado_ids=[],
        consultor_ids=[nucleo.id],
        remover_nucleado_ids=[],
        remover_consultor_ids=[],
        remover_coordenador_ids=[],
    )

    assert any("já possui o consultor" in str(err) for err in errors)


@pytest.mark.django_db
def test_validate_promocao_conflicts_bloqueia_remocao_nucleado_com_coordenacao_ativa():
    org = _create_org()
    membro = _create_user(org, "membro_4")
    nucleo = Nucleo.objects.create(organizacao=org, nome="N4")
    ParticipacaoNucleo.objects.create(
        user=membro,
        nucleo=nucleo,
        papel="coordenador",
        papel_coordenador=ParticipacaoNucleo.PapelCoordenador.COORDENADOR_GERAL,
        status="ativo",
    )

    errors, _ = validate_promocao_conflicts(
        membro=membro,
        coordenador_ids=[],
        coordenador_roles={},
        valid_action_ids={nucleo.id},
        nucleado_ids=[],
        consultor_ids=[],
        remover_nucleado_ids=[nucleo.id],
        remover_consultor_ids=[],
        remover_coordenador_ids=[],
    )

    assert any("Remova a coordenação" in str(err) for err in errors)

from __future__ import annotations

import os

import django
import pytest
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from accounts.models import UserType
from apps.backend.app.modules.membros.application.promotion_member_state import (
    sync_promocao_member_state,
)
from nucleos.models import Nucleo, ParticipacaoNucleo
from organizacoes.models import Organizacao

User = get_user_model()


def _create_org() -> Organizacao:
    return Organizacao.objects.create(
        nome=f"Org MemberState {Organizacao.objects.count()}",
        cnpj=f"99110022{Organizacao.objects.count() + 1000:04d}95",
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
def test_sync_promocao_member_state_promove_convidado_para_associado_e_limpa_nucleo():
    org = _create_org()
    nucleo = Nucleo.objects.create(organizacao=org, nome="N State 1")
    membro = _create_user(org, "state_membro_1", UserType.CONVIDADO)
    membro.nucleo = nucleo
    membro.save(update_fields=["nucleo"])

    updates = sync_promocao_member_state(
        membro=membro,
        organizacao=org,
        is_guest=True,
        promote_associado=True,
    )

    membro.refresh_from_db()
    assert "user_type" in updates
    assert "is_associado" in updates
    assert "nucleo" in updates
    assert membro.user_type == UserType.ASSOCIADO.value
    assert membro.is_associado is True
    assert membro.nucleo_id is None


@pytest.mark.django_db
def test_sync_promocao_member_state_define_coordenador_com_participacao_ativa():
    org = _create_org()
    nucleo = Nucleo.objects.create(organizacao=org, nome="N State 2")
    membro = _create_user(org, "state_membro_2", UserType.NUCLEADO)
    membro.is_coordenador = False
    membro.save(update_fields=["is_coordenador"])

    ParticipacaoNucleo.objects.create(
        user=membro,
        nucleo=nucleo,
        papel="coordenador",
        papel_coordenador=ParticipacaoNucleo.PapelCoordenador.COORDENADOR_GERAL,
        status="ativo",
    )

    updates = sync_promocao_member_state(
        membro=membro,
        organizacao=org,
        is_guest=False,
        promote_associado=False,
    )

    membro.refresh_from_db()
    assert "is_coordenador" in updates
    assert "user_type" in updates
    assert membro.is_coordenador is True
    assert membro.user_type == UserType.COORDENADOR.value


@pytest.mark.django_db
def test_sync_promocao_member_state_prioriza_consultor_sem_participacao():
    org = _create_org()
    nucleo = Nucleo.objects.create(organizacao=org, nome="N State 3")
    membro = _create_user(org, "state_membro_3", UserType.ASSOCIADO)
    nucleo.consultor = membro
    nucleo.save(update_fields=["consultor"])

    updates = sync_promocao_member_state(
        membro=membro,
        organizacao=org,
        is_guest=False,
        promote_associado=False,
    )

    membro.refresh_from_db()
    assert "user_type" in updates
    assert membro.user_type == UserType.CONSULTOR.value

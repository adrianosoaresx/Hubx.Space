import os
from datetime import timedelta

import django
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.eventos.application.public_invites import (
    create_public_invite_token,
    get_public_invite_token_generator,
    is_public_invite_token_reusable,
)
from accounts.models import UserType
from eventos.models import Evento, PreRegistroConvite
from organizacoes.models import Organizacao
from tokens.models import TokenAcesso
from tokens.services import create_invite_token

User = get_user_model()


def _create_org(nome: str, cnpj: str, created_by=None) -> Organizacao:
    return Organizacao.objects.create(nome=nome, cnpj=cnpj, created_by=created_by)


def _create_user(org: Organizacao, username: str, *, is_staff=False, is_superuser=False):
    return User.objects.create_user(
        username=username,
        email=f"{username}@hubx.local",
        password="senha123",
        user_type=UserType.ADMIN if is_staff or is_superuser else UserType.CONVIDADO,
        organizacao=org,
        is_staff=is_staff,
        is_superuser=is_superuser,
    )


def _create_evento(org: Organizacao, slug: str) -> Evento:
    inicio = timezone.now() + timedelta(days=2)
    return Evento.objects.create(
        titulo=f"Evento {slug}",
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
        participantes_maximo=100,
    )


@pytest.mark.django_db
def test_get_public_invite_token_generator_prioriza_created_by():
    owner = _create_user(_create_org("Org Owner", "12345678000195"), "owner_user")
    org = _create_org("Org Evento", "22345678000195", created_by=owner)
    evento = _create_evento(org, "evt-owner")

    generator = get_public_invite_token_generator(evento=evento, user_model=User)

    assert generator == owner


@pytest.mark.django_db
def test_get_public_invite_token_generator_fallback_staff():
    org = _create_org("Org Staff", "32345678000195")
    staff = _create_user(org, "staff_user", is_staff=True)
    evento = _create_evento(org, "evt-staff")

    generator = get_public_invite_token_generator(evento=evento, user_model=User)

    assert generator == staff


@pytest.mark.django_db
def test_is_public_invite_token_reusable_true():
    org = _create_org("Org Reuse", "42345678000195")
    gerador = _create_user(org, "gerador_reuse", is_staff=True)
    evento = _create_evento(org, "evt-reuse")
    token, codigo = create_invite_token(
        gerado_por=gerador,
        tipo_destino=TokenAcesso.TipoUsuario.CONVIDADO.value,
        organizacao=org,
        data_expiracao=timezone.now() + timedelta(days=1),
    )
    preregistro = PreRegistroConvite.objects.create(
        email="novo@invite.local",
        evento=evento,
        codigo=codigo,
        token=token,
    )

    assert is_public_invite_token_reusable(preregistro) is True


@pytest.mark.django_db
def test_create_public_invite_token_reuse_existing():
    org = _create_org("Org Reuse Existing", "52345678000195")
    gerador = _create_user(org, "gerador_existing", is_staff=True)
    evento = _create_evento(org, "evt-reuse-existing")
    token, codigo = create_invite_token(
        gerado_por=gerador,
        tipo_destino=TokenAcesso.TipoUsuario.CONVIDADO.value,
        organizacao=org,
        data_expiracao=timezone.now() + timedelta(days=1),
    )
    preregistro = PreRegistroConvite.objects.create(
        email="exists@invite.local",
        evento=evento,
        codigo=codigo,
        token=token,
    )

    reused_preregistro, reused_codigo = create_public_invite_token(
        evento=evento,
        email="exists@invite.local",
        user_model=User,
    )

    assert reused_preregistro.pk == preregistro.pk
    assert reused_codigo == codigo


@pytest.mark.django_db
def test_create_public_invite_token_creates_new_when_expired():
    org = _create_org("Org New Token", "62345678000195")
    gerador = _create_user(org, "gerador_new", is_staff=True)
    evento = _create_evento(org, "evt-new-token")
    old_token, old_codigo = create_invite_token(
        gerado_por=gerador,
        tipo_destino=TokenAcesso.TipoUsuario.CONVIDADO.value,
        organizacao=org,
        data_expiracao=timezone.now() - timedelta(days=1),
    )
    preregistro = PreRegistroConvite.objects.create(
        email="expired@invite.local",
        evento=evento,
        codigo=old_codigo,
        token=old_token,
    )

    new_preregistro, new_codigo = create_public_invite_token(
        evento=evento,
        email="expired@invite.local",
        user_model=User,
    )

    assert new_preregistro.pk == preregistro.pk
    assert new_codigo != old_codigo
    assert new_preregistro.token_id != old_token.id

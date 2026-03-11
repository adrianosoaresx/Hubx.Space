import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.membros.application.membership_policies import (
    can_access_promocao,
    parse_promote_associado_flag,
    resolve_allowed_user_types_for_creator,
    resolve_membership_target_user_type,
    should_clear_primary_nucleo,
)
from accounts.models import UserType


def test_resolve_allowed_user_types_for_creator_admin():
    assert resolve_allowed_user_types_for_creator(UserType.ADMIN.value) == [
        UserType.ASSOCIADO.value,
        UserType.OPERADOR.value,
    ]


def test_resolve_allowed_user_types_for_creator_operador():
    assert resolve_allowed_user_types_for_creator(UserType.OPERADOR.value) == [
        UserType.ASSOCIADO.value
    ]


def test_can_access_promocao():
    assert can_access_promocao(UserType.ADMIN.value)
    assert can_access_promocao(UserType.OPERADOR.value)
    assert not can_access_promocao(UserType.NUCLEADO.value)


def test_parse_promote_associado_flag():
    assert parse_promote_associado_flag("true")
    assert parse_promote_associado_flag("1")
    assert not parse_promote_associado_flag("false")


def test_resolve_membership_target_user_type_prioridade():
    assert (
        resolve_membership_target_user_type(
            current_type=UserType.NUCLEADO.value,
            has_coordenador=True,
            has_consultor=False,
            has_participacao=True,
        )
        == UserType.COORDENADOR.value
    )
    assert (
        resolve_membership_target_user_type(
            current_type=UserType.CONSULTOR.value,
            has_coordenador=False,
            has_consultor=True,
            has_participacao=False,
        )
        == UserType.CONSULTOR.value
    )


def test_should_clear_primary_nucleo():
    assert should_clear_primary_nucleo(
        has_participacao=False, has_coordenador=False, has_consultor=False
    )
    assert not should_clear_primary_nucleo(
        has_participacao=True, has_coordenador=False, has_consultor=False
    )

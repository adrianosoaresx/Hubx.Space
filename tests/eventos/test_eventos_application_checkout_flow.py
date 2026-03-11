import os
from types import SimpleNamespace

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.eventos.application.checkout_flow import (
    build_checkout_inscricao_updates,
    build_checkout_profile_data,
    build_initial_checkout_data,
    can_user_access_checkout,
    is_checkout_required,
    is_evento_gratuito,
    resolve_metodo_pagamento,
    should_block_checkout_without_confirmation,
    should_confirm_checkout_inscricao,
    should_redirect_after_checkout_approval,
)


class _EventoStub:
    def __init__(self, gratuito=False, valor=None):
        self.gratuito = gratuito
        self._valor = valor

    def get_valor_para_usuario(self, user):
        return self._valor


def test_build_checkout_profile_data_com_usuario():
    usuario = SimpleNamespace(
        get_full_name=lambda: "Usuario Nome",
        email="user@hubx.local",
        cpf="123",
        cnpj="",
        username="username",
    )

    data = build_checkout_profile_data(usuario)

    assert data == {"nome": "Usuario Nome", "email": "user@hubx.local", "documento": "123"}


def test_build_initial_checkout_data_com_inscricao_uuid():
    data = build_initial_checkout_data(
        valor_evento=150,
        checkout_profile_data={"nome": "A", "email": "a@a.com", "documento": "999"},
        default_metodo="pix",
        inscricao_uuid="abc-uuid",
    )

    assert data["valor"] == 150
    assert data["inscricao_uuid"] == "abc-uuid"
    assert data["metodo"] == "pix"


def test_is_evento_gratuito_quando_valor_zero():
    evento = _EventoStub(gratuito=False, valor=0)
    assert is_evento_gratuito(evento, user=SimpleNamespace()) is True


def test_is_checkout_required_false_sem_public_key():
    evento = _EventoStub(gratuito=False, valor=100)
    assert (
        is_checkout_required(
            evento=evento,
            user=SimpleNamespace(),
            provider_public_key="",
            metodo_pagamento="pix",
        )
        is False
    )


def test_is_checkout_required_false_para_metodo_nao_pix():
    evento = _EventoStub(gratuito=False, valor=100)
    assert (
        is_checkout_required(
            evento=evento,
            user=SimpleNamespace(),
            provider_public_key="pub",
            metodo_pagamento="boleto",
            pix_metodo="pix",
        )
        is False
    )


def test_is_checkout_required_true_para_evento_pago_com_pix():
    evento = _EventoStub(gratuito=False, valor=100)
    assert (
        is_checkout_required(
            evento=evento,
            user=SimpleNamespace(),
            provider_public_key="pub",
            metodo_pagamento="pix",
            pix_metodo="pix",
        )
        is True
    )


def test_resolve_metodo_pagamento_prioriza_valor_informado():
    transacao = SimpleNamespace(metodo="pix")
    assert resolve_metodo_pagamento(transacao, "boleto") == "boleto"


def test_resolve_metodo_pagamento_usa_transacao_quando_vazio():
    transacao = SimpleNamespace(metodo="pix")
    assert resolve_metodo_pagamento(transacao, None) == "pix"


def test_can_user_access_checkout_for_owner():
    owner = SimpleNamespace(id=1)
    assert can_user_access_checkout(
        request_user=owner,
        inscricao_user=owner,
        has_restricted_access=False,
    )


def test_can_user_access_checkout_for_restricted_access_user():
    assert can_user_access_checkout(
        request_user=SimpleNamespace(id=2),
        inscricao_user=SimpleNamespace(id=1),
        has_restricted_access=True,
    )


def test_should_redirect_after_checkout_approval():
    transacao = SimpleNamespace(status="approved")
    assert should_redirect_after_checkout_approval(transacao=transacao, approved_status="approved")
    assert not should_redirect_after_checkout_approval(transacao=transacao, approved_status="pending")


def test_should_block_checkout_without_confirmation_true():
    assert should_block_checkout_without_confirmation(
        checkout_required=True,
        transacao=None,
        metodo_pagamento=None,
    )


def test_build_checkout_inscricao_updates_with_transacao():
    transacao = SimpleNamespace(status="approved", metodo="pix")
    updates = build_checkout_inscricao_updates(
        valor_evento=120,
        transacao=transacao,
        metodo_pagamento=None,
        approved_status="approved",
    )
    assert updates["valor_pago"] == 120
    assert updates["transacao"] is transacao
    assert updates["metodo_pagamento"] == "pix"
    assert updates["pagamento_validado"] is True


def test_build_checkout_inscricao_updates_without_transacao():
    updates = build_checkout_inscricao_updates(
        valor_evento=None,
        transacao=None,
        metodo_pagamento="faturar_2x",
        approved_status="approved",
    )
    assert updates == {"metodo_pagamento": "faturar_2x"}


def test_should_confirm_checkout_inscricao():
    transacao = SimpleNamespace(status="approved")
    assert should_confirm_checkout_inscricao(transacao=transacao, approved_status="approved")
    assert not should_confirm_checkout_inscricao(transacao=transacao, approved_status="pending")

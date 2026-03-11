import os
from types import SimpleNamespace

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.notificacoes.application.delivery_planning import (
    mask_email,
    render_notification_content,
    resolve_channels_for_delivery,
    resolve_destinatario,
)
from notificacoes.models import Canal


def test_render_notification_content_interpola_contexto():
    subject, body = render_notification_content(
        subject_template="Ola {{ nome }}",
        body_template="Pedido {{ pedido_id }} confirmado",
        context={"nome": "Ana", "pedido_id": 42},
    )

    assert subject == "Ola Ana"
    assert body == "Pedido 42 confirmado"


def test_mask_email_mantem_prefixo_e_domino():
    assert mask_email("usuario@hubx.local") == "us***@hubx.local"


def test_resolve_channels_for_delivery_com_todos_e_push_sem_onesignal():
    prefs = SimpleNamespace(email=True, push=True, whatsapp=False)

    enabled, disabled = resolve_channels_for_delivery(
        template_channel=Canal.TODOS,
        prefs=prefs,
        onesignal_enabled=False,
    )

    assert enabled == [Canal.EMAIL, Canal.APP]
    assert disabled == [Canal.WHATSAPP]


def test_resolve_channels_for_delivery_push_desabilitado():
    prefs = SimpleNamespace(email=True, push=False, whatsapp=True)

    enabled, disabled = resolve_channels_for_delivery(
        template_channel=Canal.PUSH,
        prefs=prefs,
        onesignal_enabled=True,
    )

    assert enabled == []
    assert disabled == [Canal.PUSH]


def test_resolve_destinatario_email():
    user = SimpleNamespace(email="usuario@hubx.local", whatsapp="+5548999999999")
    result = resolve_destinatario(
        user=user,
        canal=Canal.EMAIL,
        push_device_lookup=lambda _user: None,
    )

    assert result == "us***@hubx.local"


def test_resolve_destinatario_push_via_lookup():
    user = SimpleNamespace(email="usuario@hubx.local", whatsapp="+5548999999999")
    result = resolve_destinatario(
        user=user,
        canal=Canal.PUSH,
        push_device_lookup=lambda _user: "device-123",
    )

    assert result == "device-123"

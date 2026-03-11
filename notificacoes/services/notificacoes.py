from __future__ import annotations

import logging
from typing import Any

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ..models import (
    Canal,
    NotificationLog,
    NotificationStatus,
    NotificationTemplate,
    UserNotificationPreference,
    PushSubscription,
)
from ..tasks import enviar_notificacao_async
from .broadcast import broadcast_notification
from apps.backend.app.modules.notificacoes.application.delivery_planning import (
    render_notification_content,
    resolve_channels_for_delivery,
    resolve_destinatario,
)

logger = logging.getLogger(__name__)


def render_template(template: NotificationTemplate, context: dict[str, Any]) -> tuple[str, str]:
    return render_notification_content(
        subject_template=template.assunto,
        body_template=template.corpo,
        context=context,
    )


def _mask_email(email: str) -> str:
    nome, _, dominio = email.partition("@")
    prefixo = nome[:2]
    return f"{prefixo}***@{dominio}" if dominio else email


def _get_destinatario(user: Any, canal: str) -> str:
    return resolve_destinatario(
        user=user,
        canal=canal,
        push_device_lookup=lambda current_user: PushSubscription.objects.filter(
            user=current_user, ativo=True
        )
        .values_list("device_id", flat=True)
        .first(),
    )


def enviar_para_usuario(
    user: Any,
    template_codigo: str,
    context: dict[str, Any],
    escopo_tipo: str | None = None,
    escopo_id: str | None = None,
) -> None:
    if not getattr(settings, "NOTIFICATIONS_ENABLED", True):
        return

    qs = NotificationTemplate.objects.filter(codigo=template_codigo, ativo=True)
    template = qs.first()
    if not template:
        raise ValueError(_("Template '%(codigo)s' não encontrado") % {"codigo": template_codigo})

    subject, body = render_template(template, context)

    prefs, _created = UserNotificationPreference.objects.get_or_create(user=user)

    canais, canais_desabilitados = resolve_channels_for_delivery(
        template_channel=template.canal,
        prefs=prefs,
        onesignal_enabled=getattr(settings, "ONESIGNAL_ENABLED", False),
    )

    for canal in canais_desabilitados:
        NotificationLog.objects.create(
            user=user,
            template=template,
            canal=canal,
            destinatario=_get_destinatario(user, canal),
            status=NotificationStatus.FALHA,
            erro=_("Canal %(canal)s desabilitado pelo usuário") % {"canal": canal},
            corpo_renderizado=body,
            context=context,
        )

    if not canais:
        return

    for canal in canais:
        log = NotificationLog.objects.create(
            user=user,
            template=template,
            canal=canal,
            destinatario=_get_destinatario(user, canal),
            corpo_renderizado=body,
            context=context,
        )

        if canal == Canal.APP:
            log.status = NotificationStatus.ENVIADA
            log.data_envio = timezone.now()
            log.save(update_fields=["status", "data_envio"])
            broadcast_notification(log, subject, body)
            continue

        enviar_notificacao_async.delay(subject, body, str(log.id))

from __future__ import annotations

from typing import Any, Callable

from django.template import Context, Template

from notificacoes.models import Canal


def render_notification_content(
    *, subject_template: str, body_template: str, context: dict[str, Any]
) -> tuple[str, str]:
    subject_tpl = Template(subject_template)
    body_tpl = Template(body_template)
    ctx = Context(context)
    return subject_tpl.render(ctx), body_tpl.render(ctx)


def mask_email(email: str) -> str:
    nome, _, dominio = email.partition("@")
    prefixo = nome[:2]
    return f"{prefixo}***@{dominio}" if dominio else email


def resolve_channels_for_delivery(
    *, template_channel: str, prefs: Any, onesignal_enabled: bool
) -> tuple[list[str], list[str]]:
    enabled: list[str] = []
    disabled: list[str] = []

    if template_channel in {Canal.EMAIL, Canal.TODOS}:
        if prefs.email:
            enabled.append(Canal.EMAIL)
        else:
            disabled.append(Canal.EMAIL)

    if template_channel in {Canal.PUSH, Canal.TODOS}:
        if prefs.push:
            enabled.append(Canal.PUSH if onesignal_enabled else Canal.APP)
        else:
            disabled.append(Canal.PUSH)

    if template_channel == Canal.APP:
        enabled.append(Canal.APP)

    if template_channel in {Canal.WHATSAPP, Canal.TODOS}:
        if prefs.whatsapp:
            enabled.append(Canal.WHATSAPP)
        else:
            disabled.append(Canal.WHATSAPP)

    return enabled, disabled


def resolve_destinatario(
    *,
    user: Any,
    canal: str,
    push_device_lookup: Callable[[Any], str | None],
) -> str:
    if canal == Canal.EMAIL:
        return mask_email(user.email)
    if canal == Canal.WHATSAPP:
        return getattr(user, "whatsapp", "")
    if canal == Canal.PUSH:
        return push_device_lookup(user) or ""
    return ""

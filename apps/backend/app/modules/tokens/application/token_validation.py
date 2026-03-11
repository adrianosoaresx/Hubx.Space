from __future__ import annotations

from django.utils.translation import gettext_lazy as _


def validate_event_token_compatibility(evento, token_obj):
    if not evento:
        return None

    if token_obj.organizacao_id and evento.organizacao_id != token_obj.organizacao_id:
        return _("Convite não corresponde ao evento informado.")

    if evento.publico_alvo != 0:
        return _("O evento não está disponível para o público geral.")

    return None


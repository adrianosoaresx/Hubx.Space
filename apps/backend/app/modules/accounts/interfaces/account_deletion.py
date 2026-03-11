from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response


def map_delete_me_invalid_confirmation_response() -> Response:
    return Response(
        {"detail": _("Senha ou confirmação inválida.")},
        status=status.HTTP_400_BAD_REQUEST,
    )

from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response


def build_created_response(*, payload: dict) -> Response:
    return Response(payload, status=status.HTTP_201_CREATED)


def build_no_content_response() -> Response:
    return Response(status=status.HTTP_204_NO_CONTENT)


def build_user_status_response(*, user, activated: bool) -> Response:
    detail = _("Usuário ativado.") if activated else _("Usuário desativado.")
    return Response(
        {
            "detail": detail,
            "id": user.id,
            "is_active": user.is_active,
        },
        status=status.HTTP_200_OK,
    )

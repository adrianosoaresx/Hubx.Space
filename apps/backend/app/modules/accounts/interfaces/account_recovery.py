from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response


def map_resend_result_to_api(result_status: str) -> Response:
    if result_status == "missing_email":
        return Response({"detail": _("Email ausente.")}, status=status.HTTP_400_BAD_REQUEST)
    if result_status == "already_active":
        return Response({"detail": _("Conta já ativada.")}, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_204_NO_CONTENT)


def map_request_password_reset_to_api(result_status: str) -> Response:
    if result_status == "missing_email":
        return Response({"detail": _("Email ausente.")}, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_204_NO_CONTENT)


def map_confirm_email_to_api(result_status: str) -> Response:
    if result_status == "missing_token":
        return Response({"detail": _("Token ausente.")}, status=status.HTTP_400_BAD_REQUEST)
    if result_status == "success":
        return Response({"detail": _("Email confirmado.")}, status=status.HTTP_200_OK)
    return Response({"detail": _("Token inválido ou expirado.")}, status=status.HTTP_400_BAD_REQUEST)


def map_reset_password_to_api(result_status: str, errors: list[str] | None) -> Response:
    if result_status == "missing_data":
        return Response({"detail": _("Dados incompletos.")}, status=status.HTTP_400_BAD_REQUEST)
    if result_status == "invalid_token":
        return Response({"detail": _("Token inválido ou expirado.")}, status=status.HTTP_400_BAD_REQUEST)
    if result_status == "invalid_password":
        return Response({"detail": errors or []}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"detail": _("Senha redefinida.")}, status=status.HTTP_200_OK)

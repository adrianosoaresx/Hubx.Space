from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response


def map_cancel_delete_result_to_api_response(*, result_status: str) -> Response | None:
    if result_status == "missing_token":
        return Response({"detail": _("Token ausente.")}, status=status.HTTP_400_BAD_REQUEST)
    if result_status != "success":
        return Response(
            {"detail": _("Token inválido ou expirado.")},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return None


def build_cancel_delete_success_response(*, user, ip: str | None, audit_logger) -> Response:
    audit_logger.log_account_delete_canceled(user=user, ip=ip)
    return Response({"detail": _("Processo cancelado.")})

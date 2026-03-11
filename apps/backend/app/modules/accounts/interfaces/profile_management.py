from __future__ import annotations

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response

from apps.backend.app.modules.accounts.domain.exceptions import (
    InvalidProfileSectionError,
    ProfileManagementPermissionDeniedError,
    UserAlreadyActiveError,
    UserAlreadyInactiveError,
)


def map_domain_error_to_http_response(error: Exception) -> HttpResponse:
    if isinstance(error, ProfileManagementPermissionDeniedError):
        raise PermissionDenied
    if isinstance(error, UserAlreadyActiveError):
        return HttpResponseBadRequest(_("Usuário já está ativo."))
    if isinstance(error, UserAlreadyInactiveError):
        return HttpResponseBadRequest(_("Usuário já está inativo."))
    if isinstance(error, InvalidProfileSectionError):
        return HttpResponseBadRequest("Invalid section")
    raise error


def map_domain_error_to_api_response(error: Exception) -> Response:
    if isinstance(error, ProfileManagementPermissionDeniedError):
        return Response(
            {"detail": _("Sem permissão para gerenciar este perfil.")},
            status=status.HTTP_403_FORBIDDEN,
        )
    if isinstance(error, UserAlreadyActiveError):
        return Response({"detail": _("Usuário já está ativo.")}, status=status.HTTP_400_BAD_REQUEST)
    if isinstance(error, UserAlreadyInactiveError):
        return Response({"detail": _("Usuário já está inativo.")}, status=status.HTTP_400_BAD_REQUEST)
    if isinstance(error, InvalidProfileSectionError):
        return Response({"detail": "Invalid section"}, status=status.HTTP_400_BAD_REQUEST)
    raise error

from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response


def map_2fa_password_invalid_response() -> Response:
    return Response({"detail": _("Senha incorreta.")}, status=status.HTTP_400_BAD_REQUEST)


def map_2fa_already_enabled_response() -> Response:
    return Response({"detail": _("2FA já habilitado.")}, status=status.HTTP_400_BAD_REQUEST)


def map_2fa_code_required_response() -> Response:
    return Response({"detail": _("Código obrigatório.")}, status=status.HTTP_400_BAD_REQUEST)


def map_2fa_invalid_code_response() -> Response:
    return Response({"detail": _("Código inválido.")}, status=status.HTTP_400_BAD_REQUEST)


def build_2fa_setup_secret_response(*, otp_uri: str, secret: str) -> Response:
    return Response({"otpauth_url": otp_uri, "secret": secret})


def map_2fa_enabled_response() -> Response:
    return Response({"detail": _("2FA habilitado.")})


def map_2fa_disabled_response() -> Response:
    return Response({"detail": _("2FA desabilitado.")})

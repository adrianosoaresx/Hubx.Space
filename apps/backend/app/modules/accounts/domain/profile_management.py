from __future__ import annotations

from accounts.models import UserType

from .exceptions import (
    InvalidProfileSectionError,
    ProfileManagementPermissionDeniedError,
    UserAlreadyActiveError,
    UserAlreadyInactiveError,
)

ALLOWED_PROFILE_SECTIONS = {"info"}
TOGGLE_ACTIVE_ALLOWED_TYPES = {
    UserType.ROOT.value,
    UserType.ADMIN.value,
    UserType.OPERADOR.value,
}


def ensure_manage_permission(viewer, profile, *, can_manage_profile) -> None:
    if not can_manage_profile(viewer, profile):
        raise ProfileManagementPermissionDeniedError("Sem permissao para gerenciar este perfil.")


def ensure_can_toggle_user_active(viewer, profile, *, can_manage_profile) -> None:
    ensure_manage_permission(viewer, profile, can_manage_profile=can_manage_profile)
    viewer_type = getattr(viewer, "get_tipo_usuario", None)
    if viewer_type not in TOGGLE_ACTIVE_ALLOWED_TYPES:
        raise ProfileManagementPermissionDeniedError("Sem permissao para alterar status deste usuario.")


def ensure_can_activate_user(profile) -> None:
    if profile.is_active:
        raise UserAlreadyActiveError("Usuario ja esta ativo.")


def ensure_can_deactivate_user(profile) -> None:
    if not profile.is_active:
        raise UserAlreadyInactiveError("Usuario ja esta inativo.")


def resolve_profile_section_template(section: str, *, can_manage: bool) -> str:
    if section not in ALLOWED_PROFILE_SECTIONS:
        raise InvalidProfileSectionError("Invalid section")
    if section == "info":
        return (
            "perfil/partials/detail_informacoes.html"
            if can_manage
            else "perfil/partials/publico_informacoes.html"
        )
    raise InvalidProfileSectionError("Invalid section")

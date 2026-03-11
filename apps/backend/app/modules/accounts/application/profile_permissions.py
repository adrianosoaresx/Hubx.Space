from __future__ import annotations

from accounts.models import UserType


def can_manage_profile(viewer, profile) -> bool:
    if viewer is None or not getattr(viewer, "is_authenticated", False):
        return False
    if viewer == profile:
        return True

    viewer_type = getattr(viewer, "get_tipo_usuario", None)
    if viewer_type == UserType.ROOT.value:
        return True

    if viewer_type in {UserType.ADMIN.value, UserType.OPERADOR.value}:
        viewer_org = getattr(viewer, "organizacao_id", None)
        profile_org = getattr(profile, "organizacao_id", None)
        return viewer_org is not None and viewer_org == profile_org

    return False


def can_promote_profile(viewer, profile) -> bool:
    if viewer is None or not getattr(viewer, "is_authenticated", False):
        return False

    viewer_type = getattr(viewer, "get_tipo_usuario", None)
    if viewer_type not in {UserType.ADMIN.value, UserType.OPERADOR.value}:
        return False

    profile_type_attr = getattr(profile, "get_tipo_usuario", None)
    profile_type = profile_type_attr() if callable(profile_type_attr) else profile_type_attr
    if profile_type in {UserType.ADMIN.value, UserType.OPERADOR.value}:
        return False

    viewer_org = getattr(viewer, "organizacao_id", None)
    profile_org = getattr(profile, "organizacao_id", None)
    return viewer_org is not None and profile_org is not None and viewer_org == profile_org


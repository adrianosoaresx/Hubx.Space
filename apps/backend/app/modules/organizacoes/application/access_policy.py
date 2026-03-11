from __future__ import annotations

from accounts.models import UserType


def apply_admin_org_scope(queryset, user):
    if getattr(user, "user_type", None) == UserType.ADMIN:
        return queryset.filter(pk=getattr(user, "organizacao_id", None))
    return queryset


def apply_user_org_scope(queryset, user):
    org_id = getattr(user, "organizacao_id", None)
    if org_id:
        return queryset.filter(pk=org_id)
    return queryset


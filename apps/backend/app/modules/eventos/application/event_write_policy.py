from __future__ import annotations

from typing import Any

from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Model
from django.db.models.fields.files import FieldFile
from django.utils.functional import Promise

from accounts.models import UserType


def ensure_user_can_create_evento(user_type: str | None) -> None:
    if user_type == UserType.ROOT.value:
        raise PermissionDenied("Usuário root não pode criar eventos.")


def ensure_coordinator_can_use_nucleo(
    *,
    user_type: str | None,
    allowed_nucleo_ids: list[int] | tuple[int, ...] | set[int] | None,
    nucleo_id: int | None,
) -> None:
    if user_type != UserType.COORDENADOR.value:
        return
    if not nucleo_id:
        return
    if nucleo_id not in set(allowed_nucleo_ids or []):
        raise PermissionDenied("Coordenadores só podem criar eventos dos núcleos que coordenam.")


def apply_coordinator_nucleo_scope(queryset, *, user_type: str | None, allowed_nucleo_ids):
    if user_type != UserType.COORDENADOR.value:
        return queryset
    if not allowed_nucleo_ids:
        return queryset.none()
    return queryset.filter(nucleo_id__in=allowed_nucleo_ids)


def serialize_evento_change_value(value: Any) -> Any:
    if isinstance(value, Promise):
        return str(value)
    if isinstance(value, FieldFile):
        return value.name if value else None
    if isinstance(value, UploadedFile):
        return value.name
    if isinstance(value, Model):
        return {"id": value.pk, "repr": str(value)}
    if isinstance(value, dict):
        return {key: serialize_evento_change_value(val) for key, val in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [serialize_evento_change_value(val) for val in value]
    return value


def build_evento_change_details(*, old_obj: Any, cleaned_data: dict[str, Any], changed_fields: list[str]) -> dict[str, dict[str, Any]]:
    details: dict[str, dict[str, Any]] = {}
    for field in changed_fields:
        before = getattr(old_obj, field)
        after = cleaned_data.get(field)
        if before == after:
            continue
        details[field] = {
            "antes": serialize_evento_change_value(before),
            "depois": serialize_evento_change_value(after),
        }
    return details

from __future__ import annotations

from datetime import date

from accounts.models import UserType


def parse_dia_iso(dia_iso: str | None) -> tuple[date | None, str | None]:
    if not dia_iso:
        return None, "Parâmetro 'dia' obrigatório."
    try:
        return date.fromisoformat(dia_iso), None
    except ValueError:
        return None, "Data inválida."


def user_can_view_eventos_por_dia(user_type: str | None) -> bool:
    return user_type != UserType.ROOT


def build_eventos_por_dia_context(
    *,
    dia: date,
    eventos: list,
    title: object,
    subtitle: object = None,
) -> dict[str, object]:
    return {"dia": dia, "eventos": eventos, "title": title, "subtitle": subtitle}


def get_eventos_por_dia_template() -> str:
    return "eventos/partials/calendario/_lista_eventos_dia.html"

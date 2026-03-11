from __future__ import annotations

from decimal import Decimal

from accounts.models import UserType


ORCAMENTO_FIELDS = ("orcamento_estimado", "valor_gasto")


def user_can_manage_evento_orcamento(tipo_usuario: str | None) -> bool:
    return tipo_usuario in {UserType.ADMIN.value, UserType.COORDENADOR.value}


def parse_orcamento_payload(post_data) -> tuple[dict[str, Decimal], dict[str, str]]:
    dados: dict[str, Decimal] = {}
    errors: dict[str, str] = {}

    for field in ORCAMENTO_FIELDS:
        if field in post_data and post_data.get(field) != "":
            raw = post_data.get(field)
            try:
                dados[field] = Decimal(str(raw))
            except Exception:
                errors[field] = "valor inválido"
    return dados, errors


def apply_orcamento_changes(evento, dados: dict[str, Decimal]) -> tuple[dict[str, dict[str, str | None]], list[str]]:
    alteracoes: dict[str, dict[str, str | None]] = {}
    update_fields: list[str] = []

    for field, novo_valor in dados.items():
        antigo_valor = getattr(evento, field)
        if antigo_valor != novo_valor:
            alteracoes[field] = {
                "antes": f"{antigo_valor:.2f}" if antigo_valor is not None else None,
                "depois": f"{novo_valor:.2f}",
            }
            setattr(evento, field, novo_valor)
            update_fields.append(field)

    return alteracoes, update_fields


def should_persist_orcamento_changes(alteracoes: dict[str, dict[str, str | None]]) -> bool:
    return bool(alteracoes)


def build_orcamento_success_payload(alteracoes: dict[str, dict[str, str | None]]) -> dict[str, object]:
    return {"status": "ok", "alteracoes": alteracoes}

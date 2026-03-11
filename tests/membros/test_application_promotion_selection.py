import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.membros.application.promotion_selection import (
    build_promocao_selection,
    extract_coordenador_role_values,
    parse_unique_int_ids,
)


def test_parse_unique_int_ids_remove_invalidos_duplicados():
    assert parse_unique_int_ids(["1", "a", "2", "1", "", "3"]) == [1, 2, 3]


def test_extract_coordenador_role_values_filtra_prefixo():
    raw = {
        "coordenador_papel_1": "coordenador_geral",
        "coordenador_papel_2": " vice_coordenador ",
        "outro": "x",
    }
    assert extract_coordenador_role_values(raw) == {
        "1": "coordenador_geral",
        "2": "vice_coordenador",
    }


def test_build_promocao_selection_compose_campos():
    selection = build_promocao_selection(
        raw_nucleado=["1", "1", "x"],
        raw_consultor=["2"],
        raw_coordenador=["3", "4"],
        raw_remover_nucleado=["4"],
        raw_remover_consultor=[],
        raw_remover_coordenador=["2"],
        role_values_by_nucleo={"3": "coordenador_geral", "4": ""},
    )

    assert selection.nucleado_ids == [1]
    assert selection.consultor_ids == [2]
    assert selection.coordenador_ids == [3, 4]
    assert selection.remover_nucleado_ids == [4]
    assert selection.remover_coordenador_ids == [2]
    assert selection.selected_coordenador_roles == {"3": "coordenador_geral", "4": ""}
    assert selection.coordenador_roles == {3: "coordenador_geral"}
    assert selection.all_selected_ids == {1, 2, 3, 4}
    assert selection.all_action_ids == {1, 2, 3, 4}

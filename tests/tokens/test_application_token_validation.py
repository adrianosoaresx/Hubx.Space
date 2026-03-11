from types import SimpleNamespace

from apps.backend.app.modules.tokens.application.token_validation import (
    validate_event_token_compatibility,
)


def _evento(**kwargs):
    data = {"organizacao_id": "org-1", "publico_alvo": 0}
    data.update(kwargs)
    return SimpleNamespace(**data)


def _token(**kwargs):
    data = {"organizacao_id": "org-1"}
    data.update(kwargs)
    return SimpleNamespace(**data)


def test_validate_event_token_compatibility_allows_matching_org_and_public():
    assert validate_event_token_compatibility(_evento(), _token()) is None


def test_validate_event_token_compatibility_blocks_org_mismatch():
    message = validate_event_token_compatibility(_evento(organizacao_id="org-2"), _token(organizacao_id="org-1"))
    assert str(message) == "Convite não corresponde ao evento informado."


def test_validate_event_token_compatibility_blocks_non_public_event():
    message = validate_event_token_compatibility(_evento(publico_alvo=1), _token())
    assert str(message) == "O evento não está disponível para o público geral."


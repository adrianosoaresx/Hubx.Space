# Onda 2 - Iteracao Eventos Event Write Policy

Data: 2026-03-10 14:38:55

## Escopo executado
- Extracao de politica de escrita de eventos para camada `application`:
  - `apps/backend/app/modules/eventos/application/event_write_policy.py`
    - `ensure_user_can_create_evento`
    - `ensure_coordinator_can_use_nucleo`
    - `apply_coordinator_nucleo_scope`
    - `serialize_evento_change_value`
    - `build_evento_change_details`
- Delegacao aplicada em `eventos/views.py`:
  - `EventoCreateView.dispatch`
  - `EventoCreateView.form_valid`
  - `EventoUpdateView.get_queryset`
  - `EventoUpdateView.form_valid`
  - `EventoDeleteView.get_queryset`

## Testes adicionados
- `tests/eventos/test_eventos_application_event_write_policy.py`

## Correcao adicional identificada no smoke
- Ajuste de templates com tag `static` sem carregamento da biblioteca:
  - `eventos/templates/eventos/partials/eventos/_form_fields.html`
  - `eventos/templates/eventos/partials/evento_delete_modal.html`

## Validacao
- `.\.venv\Scripts\python.exe manage.py check` OK
- Suite direcionada Onda 2: 84 passed, 4 warnings
- Smoke funcional com usuario de negocio com organizacao/permissoes validas:
  - `docs/etapas/smoke_onda2_eventos_event_write_policy_20260310_143855.md`

## Observacao
- As regras de permissao e escopo de coordenador continuam preservadas, agora centralizadas na camada `application`, reduzindo duplicacao entre create/update/delete.

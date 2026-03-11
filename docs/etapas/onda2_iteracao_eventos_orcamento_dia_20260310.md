# Onda 2 - Iteracao Eventos Orcamento e Listagem por Dia

Data: 2026-03-10 14:19:21

## Escopo executado
- Extracao de regras de orcamento para camada `application`:
  - `apps/backend/app/modules/eventos/application/budget_rules.py`
    - `user_can_manage_evento_orcamento`
    - `parse_orcamento_payload`
    - `apply_orcamento_changes`
- Extracao de regras de listagem por dia:
  - `apps/backend/app/modules/eventos/application/day_listing.py`
    - `parse_dia_iso`
    - `user_can_view_eventos_por_dia`
- Delegacao aplicada em `eventos/views.py`:
  - `evento_orcamento`
  - `eventos_por_dia`

## Testes adicionados
- `tests/eventos/test_eventos_application_budget_rules.py`
- `tests/eventos/test_eventos_application_day_listing.py`

## Validacao
- `python manage.py check` OK
- Suite direcionada Onda 2: 63 passed, 4 warnings
- Smoke funcional com usuario de negocio:
  - `docs/etapas/smoke_onda2_eventos_orcamento_dia_20260310_141908.md`

## Observacao
- O smoke executou POST real em `evento_orcamento` e registrou alteracoes de `orcamento_estimado` e `valor_gasto` no evento de teste da organizacao.

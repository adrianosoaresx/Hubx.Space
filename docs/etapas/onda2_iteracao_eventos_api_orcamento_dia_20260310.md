# Onda 2 - Iteracao Eventos API Orcamento e Dia

Data: 2026-03-10 15:20:53

## Escopo executado
- Extracao complementar das APIs auxiliares para camada `application`:
  - `apps/backend/app/modules/eventos/application/budget_rules.py`
    - `should_persist_orcamento_changes`
    - `build_orcamento_success_payload`
  - `apps/backend/app/modules/eventos/application/day_listing.py`
    - `build_eventos_por_dia_context`
    - `get_eventos_por_dia_template`
- Delegacao aplicada em `eventos/views.py`:
  - `evento_orcamento`
  - `eventos_por_dia`

## Testes atualizados
- `tests/eventos/test_eventos_application_budget_rules.py`
- `tests/eventos/test_eventos_application_day_listing.py`

## Validacao
- `.\.venv\Scripts\python.exe manage.py check` OK
- Suite direcionada Onda 2: 120 passed, 4 warnings
- Smoke funcional com usuario de negocio com organizacao/permissoes validas:
  - `docs/etapas/smoke_onda2_eventos_api_orcamento_dia_20260310_152053.md`

## Observacao
- O smoke confirmou payload JSON esperado para alteracoes de orcamento e retorno do endpoint de eventos por dia, com rollback controlado para restaurar valores originais.

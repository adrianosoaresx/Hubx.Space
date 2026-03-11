# Onda 2 - Iteracao Eventos Portfolio Context

Data: 2026-03-10 15:28:34

## Escopo executado
- Extracao do estado de portfolio do detalhe de evento para camada `application`:
  - `apps/backend/app/modules/eventos/application/portfolio_context.py`
    - `resolve_portfolio_query`
    - `resolve_portfolio_show_form`
    - `resolve_portfolio_selection_state`
    - `resolve_portfolio_navigation_state`
- Delegacao aplicada em `eventos/views.py`:
  - `EventoDetailView.get_context_data` (blocos de query de filtro, flags de exibicao do formulario, selecao de midia e navegacao de retorno)

## Testes adicionados
- `tests/eventos/test_eventos_application_portfolio_context.py`

## Validacao
- `.\.venv\Scripts\python.exe manage.py check` OK
- Suite direcionada Onda 2: 129 passed, 4 warnings
- Smoke funcional com usuario de negocio com organizacao/permissoes validas:
  - `docs/etapas/smoke_onda2_eventos_portfolio_context_20260310_152834.md`

## Observacao
- O smoke cobriu cenarios com e sem midia para validar as transicoes de estado de portfolio sem regressao no detalhe do evento.

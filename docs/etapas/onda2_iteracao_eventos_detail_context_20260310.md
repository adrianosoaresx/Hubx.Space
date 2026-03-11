# Onda 2 - Iteracao Eventos Detail Context

Data: 2026-03-10 15:01:22

## Escopo executado
- Extracao de regras de contexto do detalhe de evento para camada `application`:
  - `apps/backend/app/modules/eventos/application/event_detail_context.py`
    - `resolve_event_management_permissions`
    - `sort_inscricoes_financeiro`
    - `build_inscricao_status_summary`
    - `build_financeiro_summary`
- Delegacao aplicada em `eventos/views.py`:
  - `EventoDetailView.get_context_data` (blocos de permissao de gestao, ordenacao financeiro e sumarios de inscricoes/pagamentos)

## Testes adicionados
- `tests/eventos/test_eventos_application_event_detail_context.py`

## Validacao
- `.\.venv\Scripts\python.exe manage.py check` OK
- Suite direcionada Onda 2: 107 passed, 4 warnings
- Smoke funcional com usuario de negocio com organizacao/permissoes validas:
  - `docs/etapas/smoke_onda2_eventos_detail_context_20260310_150122.md`

## Observacao
- A montagem do contexto de `EventoDetailView` ficou menos acoplada e mais testavel, mantendo as mesmas respostas HTTP/fluxos em detalhe, inscritos, convites e portfolio.

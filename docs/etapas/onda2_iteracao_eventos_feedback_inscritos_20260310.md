# Onda 2 - Iteracao Eventos Feedback e Inscritos

Data: 2026-03-10 14:25:23

## Escopo executado
- Extracao de regras de engajamento para camada `application`:
  - `apps/backend/app/modules/eventos/application/engagement_rules.py`
    - `can_user_rate_event`
    - `can_cancelar_inscricao`
    - `parse_feedback_nota`
- Extracao de regras de preparacao de inscritos para relatorio:
  - `apps/backend/app/modules/eventos/application/inscritos_reporting.py`
    - `resolve_participante_nome`
    - `inscricao_sort_key`
    - `prepare_inscricoes_for_report`
- Delegacao aplicada em `eventos/views.py`:
  - `EventoDetailView.get_context_data` (avaliacao_permitida / pode_cancelar)
  - `EventoInscritosPDFView.get`
  - `EventoFeedbackView.get` e `EventoFeedbackView.post`
  - helper `_resolve_participante_nome`

## Testes adicionados
- `tests/eventos/test_eventos_application_engagement_rules.py`
- `tests/eventos/test_eventos_application_inscritos_reporting.py`

## Validacao
- `python manage.py check` OK
- Suite direcionada Onda 2: 72 passed, 4 warnings
- Smoke funcional com usuario de negocio em fluxo de feedback e inscritos:
  - `docs/etapas/smoke_onda2_eventos_feedback_inscritos_20260310_142512.md`

## Observacao
- O smoke executou `POST /eventos/evento/<id>/feedback/` com nota valida e recebeu redirect de sucesso para detalhe do evento (`302`), preservando o comportamento esperado.

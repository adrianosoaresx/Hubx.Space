# Onda 2 - Iteracao Eventos Briefing Flow

Data: 2026-03-10 14:33:01

## Escopo executado
- Extracao de regras do fluxo de briefing para camada `application`:
  - `apps/backend/app/modules/eventos/application/briefing_flow.py`
    - `get_evento_briefing`
    - `build_briefing_select_initial`
    - `apply_briefing_template_selection`
- Delegacao aplicada em `eventos/views.py`:
  - `BriefingTemplateSelectView.get_form`
  - `BriefingTemplateSelectView.post`
  - `BriefingEventoFillView.dispatch`

## Testes adicionados
- `tests/eventos/test_eventos_application_briefing_flow.py`

## Validacao
- `.\.venv\Scripts\python.exe manage.py check` OK
- Suite direcionada Onda 2: 76 passed, 4 warnings
- Smoke funcional com usuario de negocio com organizacao/permissoes validas:
  - `docs/etapas/smoke_onda2_eventos_briefing_flow_20260310_143301.md`

## Observacao
- O `POST /eventos/eventos/<uuid>/briefing/selecionar/` retornou `302` para a tela de preenchimento (`/briefing/preencher/`), e o registro de `BriefingEvento` permaneceu consistente com `template_id` selecionado.

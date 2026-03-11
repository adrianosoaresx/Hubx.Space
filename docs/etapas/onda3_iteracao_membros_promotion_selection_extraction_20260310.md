# Onda 3.2 - Iteracao Membros Promotion Selection Extraction

Data: 2026-03-10
Status: concluido

## Objetivo
Extrair parsing/composição dos comandos de promoção/remoção de `MembroPromoverFormView.post` para `application`, preparando a próxima etapa de extração da persistência transacional.

## Entregas
- Novo módulo application:
  - `apps/backend/app/modules/membros/application/promotion_selection.py`
    - `parse_unique_int_ids`
    - `extract_coordenador_role_values`
    - `build_promocao_selection`
    - `PromotionSelection` (objeto de composição)
- Refactor em `membros/views.py`:
  - remoção do parsing inline de IDs/roles
  - uso de `build_promocao_selection` para compor:
    - seleções de promoção/remoção
    - mapa de papéis de coordenação
    - conjuntos agregados (`all_selected_ids`, `all_action_ids`)

## Testes adicionados
- `tests/membros/test_application_promotion_selection.py`
  - valida parsing de inteiros com deduplicação
  - extração de papéis por prefixo de campo
  - composição completa do objeto de seleção

## Validação técnica
- `./.venv/Scripts/python.exe manage.py check` -> OK
- `./.venv/Scripts/python.exe -m pytest tests/membros -q` -> 19 passed
- Regressão dirigida plataforma:
  - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q` -> 76 passed
- Smoke funcional registrado em:
  - `docs/etapas/smoke_onda3_membros_promotion_selection_parsing_20260310_163638.md`

## Riscos e trade-offs
- Trade-off: esta fatia foca exclusivamente no parsing/composição; a mutação em banco permanece na view para reduzir risco imediato.
- Risco residual: ainda existe bloco transacional grande na view, alvo do próximo slice.

## Rollback local (sem Git)
1. Remover `apps/backend/app/modules/membros/application/promotion_selection.py`.
2. Reverter `membros/views.py` para parsing inline anterior.
3. Remover `tests/membros/test_application_promotion_selection.py`.
4. Reexecutar:
   - `./.venv/Scripts/python.exe manage.py check`
   - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q`

## Próximo passo recomendado
Próxima fatia de `membros`: extrair aplicação transacional de promoções/remoções (persistência de `ParticipacaoNucleo` e vínculo de consultor) para `application`, mantendo a view como orquestradora HTTP.

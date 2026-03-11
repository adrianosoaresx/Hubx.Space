# Onda 3.2 - Iteracao Membros Promotion Member State Extraction

Data: 2026-03-10
Status: concluido

## Objetivo
Extrair a atualização de estado final do membro após promoção para a camada `application`, reduzindo regra de domínio na view.

## Entregas
- Novo módulo application:
  - `apps/backend/app/modules/membros/application/promotion_member_state.py`
    - `sync_promocao_member_state`
    - responsabilidades:
      - cálculo de vínculos ativos (participação, coordenação, consultoria)
      - promoção de convidado para associado
      - atualização de `is_coordenador`
      - limpeza de núcleo principal quando necessário
      - ajuste de `user_type` final por política de membership
- Refactor em `membros/views.py`:
  - remoção do bloco inline de pós-persistência
  - view delega para `sync_promocao_member_state(...)`

## Testes adicionados
- `tests/membros/test_application_promotion_member_state.py`
  - convidado -> associado com limpeza de núcleo
  - definição de coordenador quando há participação ativa coordenador
  - priorização de tipo consultor sem participação ativa

## Validação técnica
- `./.venv/Scripts/python.exe manage.py check` -> OK
- `./.venv/Scripts/python.exe -m pytest tests/membros/test_application_promotion_member_state.py -q` -> 3 passed
- `./.venv/Scripts/python.exe -m pytest tests/membros -q` -> 25 passed
- Regressão dirigida plataforma:
  - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q` -> 82 passed
- Smoke funcional registrado em:
  - `docs/etapas/smoke_onda3_membros_promotion_member_state_20260310_165338.md`

## Riscos e trade-offs
- Trade-off: `application` segue orientada a modelos Django para manter migração incremental segura.
- Risco residual: `MembroPromoverFormView` ainda concentra validação de request/contexto da tela; potencial próxima extração para `interfaces` + DTO.

## Rollback local (sem Git)
1. Remover `apps/backend/app/modules/membros/application/promotion_member_state.py`.
2. Restaurar bloco pós-persistência original em `membros/views.py`.
3. Remover `tests/membros/test_application_promotion_member_state.py`.
4. Reexecutar:
   - `./.venv/Scripts/python.exe manage.py check`
   - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q`

## Próximo passo recomendado
Extrair montagem de contexto da tela de promoção (`_build_form_context`) para `application/query service`, reduzindo tamanho da view e isolando lógica de leitura.

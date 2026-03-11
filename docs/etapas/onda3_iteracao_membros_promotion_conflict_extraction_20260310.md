# Onda 3.2 - Iteracao Membros Promotion Conflict Extraction

Data: 2026-03-10
Status: concluido

## Objetivo
Extrair validações de conflito do fluxo de promoção (`MembroPromoverFormView.post`) para `application`, mantendo persistência transacional na view e reduzindo complexidade/duplicação.

## Entregas
- Novo módulo application:
  - `apps/backend/app/modules/membros/application/promotion_conflicts.py`
    - `validate_promocao_conflicts`
    - validações extraídas:
      - papel obrigatório/válido para coordenação
      - papel de coordenação já ocupado no núcleo
      - restrição de papéis exclusivos (`coordenador_geral`/`vice_coordenador`)
      - conflitos de promover/remover no mesmo núcleo
      - conflito consultor x coordenador no mesmo núcleo
      - núcleo com consultor já ocupado
      - bloqueio de remoção de nucleado com coordenação ativa não removida
- Refactor em `membros/views.py`:
  - bloco de validação de conflito delegado para `validate_promocao_conflicts`
  - view mantém orquestração de contexto/retorno HTTP e bloco de persistência.

## Testes adicionados
- `tests/membros/test_application_promotion_conflicts.py`
  - cobre papel obrigatório, sobreposição consultor/coordenador, consultor ocupado e bloqueio de remoção com coordenação ativa.

## Validação técnica
- `./.venv/Scripts/python.exe manage.py check` -> OK
- `./.venv/Scripts/python.exe -m pytest tests/membros -q` -> 16 passed
- Regressão dirigida plataforma:
  - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q` -> 73 passed
- Smoke funcional registrado em:
  - `docs/etapas/smoke_onda3_membros_promocao_conflict_validation_20260310_163256.md`

## Riscos e trade-offs
- Trade-off: extração focada em validações; persistência e atualização de entidades continuam na view para preservar estabilidade nesta fatia.
- Risco residual: `MembroPromoverFormView.post` ainda é extenso e deve ser quebrado em mais dois slices (parse/composição de comandos e aplicação transacional).

## Rollback local (sem Git)
1. Remover `apps/backend/app/modules/membros/application/promotion_conflicts.py`.
2. Reverter `membros/views.py` para validações inline anteriores.
3. Remover `tests/membros/test_application_promotion_conflicts.py`.
4. Reexecutar:
   - `./.venv/Scripts/python.exe manage.py check`
   - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q`

## Próximo passo recomendado
Próxima fatia em `membros`: extrair parsing/composição de seleção de núcleos e papéis (nucleado/consultor/coordenador/remoções) para `application`, reduzindo ainda mais a complexidade da view antes de mover persistência.

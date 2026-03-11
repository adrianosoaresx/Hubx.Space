# Onda 3.2 - Iteracao Membros Promotion Persistence Extraction

Data: 2026-03-10
Status: concluido

## Objetivo
Extrair a mutação transacional de promoção/remoção de `MembroPromoverFormView.post` para a camada `application`, reduzindo acoplamento HTTP + regra de persistência.

## Entregas
- Novo módulo application:
  - `apps/backend/app/modules/membros/application/promotion_persistence.py`
    - `apply_promocao_persistence`
    - Operações consolidadas:
      - atribuição/remoção de consultor em `Nucleo`
      - criação/atualização de `ParticipacaoNucleo`
      - remoção de coordenação
      - remoção de nucleado (inativação)
- Refactor em `membros/views.py`:
  - remoção do bloco transacional inline
  - view passou a orquestrar validação + chamada de `apply_promocao_persistence`

## Testes adicionados
- `tests/membros/test_application_promotion_persistence.py`
  - promoção para coordenador + consultor com reativação
  - criação de participação para nucleado
  - remoção de consultor/coordenador/nucleado no mesmo fluxo

## Validação técnica
- `./.venv/Scripts/python.exe manage.py check` -> OK
- `./.venv/Scripts/python.exe -m pytest tests/membros/test_application_promotion_persistence.py -q` -> 3 passed
- `./.venv/Scripts/python.exe -m pytest tests/membros -q` -> 22 passed
- Regressão dirigida plataforma:
  - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q` -> 79 passed
- Smoke funcional registrado em:
  - `docs/etapas/smoke_onda3_membros_promotion_persistence_20260310_164822.md`

## Riscos e trade-offs
- Trade-off: a camada `application` ainda manipula modelos Django diretamente (passo incremental para reduzir risco de regressão).
- Risco residual: regras de transição de tipo de usuário (`user_type`) e `nucleo` principal permanecem na view e podem ser extraídas em fatia futura.

## Rollback local (sem Git)
1. Remover `apps/backend/app/modules/membros/application/promotion_persistence.py`.
2. Restaurar o bloco transacional original em `membros/views.py`.
3. Remover `tests/membros/test_application_promotion_persistence.py`.
4. Reexecutar:
   - `./.venv/Scripts/python.exe manage.py check`
   - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q`

## Próximo passo recomendado
Extrair atualização de estado de membro pós-persistência (`is_coordenador`, `user_type`, `nucleo` principal) para `application`, mantendo o mesmo padrão de smoke com usuário de negócio válido.

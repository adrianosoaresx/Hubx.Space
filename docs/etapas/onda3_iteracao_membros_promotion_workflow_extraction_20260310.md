# Onda 3.2 - Iteracao Membros Promotion Workflow Extraction

Data: 2026-03-10
Status: concluido

## Objetivo
Consolidar o comando completo de promoção em um único use-case de `application`, deixando a view como adapter HTTP/HTMX.

## Entregas
- Novo use-case:
  - `apps/backend/app/modules/membros/application/promotion_workflow.py`
    - `execute_promocao_from_post`
    - `execute_promocao_workflow`
    - `PromocaoWorkflowResult`
  - Orquestra:
    - parsing/seleção de payload
    - validações de conflito e núcleos válidos
    - persistência transacional
    - sincronização de estado final do membro
- Refactor em `membros/views.py`:
  - `post` simplificado para:
    - chamar `execute_promocao_from_post`
    - renderizar contexto de erro/sucesso com base no resultado

## Testes adicionados
- `tests/membros/test_application_promotion_workflow.py`
  - erro de coordenação sem papel (400 lógico)
  - fluxo válido de promoção nucleado + sync de estado

## Validação técnica
- `./.venv/Scripts/python.exe manage.py check` -> OK
- `./.venv/Scripts/python.exe -m pytest tests/membros/test_application_promotion_workflow.py -q` -> 2 passed
- `./.venv/Scripts/python.exe -m pytest tests/membros -q` -> 29 passed
- Regressão dirigida plataforma:
  - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q` -> 86 passed
- Smoke funcional registrado em:
  - `docs/etapas/smoke_onda3_membros_promotion_workflow_20260310_170417.md`

## Riscos e trade-offs
- Trade-off: o use-case recebe `post_data` para reduzir fricção da extração; ganho de velocidade agora, com possível evolução futura para DTO explícito.
- Risco residual: ainda há mensagens/i18n e estrutura de contexto espalhadas entre workflow e builder de contexto.

## Rollback local (sem Git)
1. Remover `apps/backend/app/modules/membros/application/promotion_workflow.py`.
2. Restaurar lógica inline anterior no `post` de `membros/views.py`.
3. Remover `tests/membros/test_application_promotion_workflow.py`.
4. Reexecutar:
   - `./.venv/Scripts/python.exe manage.py check`
   - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q`

## Próximo passo recomendado
Padronizar o retorno dos use-cases de `membros` em contratos internos (DTO de entrada/saída), para reduzir dependência de `QueryDict` e facilitar testes de interface.

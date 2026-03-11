# Onda 3.2 - Iteracao Membros Promotion Workflow DTO Contract

Data: 2026-03-10
Status: concluido

## Objetivo
Padronizar contrato interno do workflow de promoção para reduzir dependência de `QueryDict` e melhorar testabilidade da camada `application`.

## Entregas
- Evolução de `apps/backend/app/modules/membros/application/promotion_workflow.py`:
  - novo DTO de entrada `PromocaoWorkflowInput`
  - novo `Protocol` `PostDataLike` para adapter HTTP
  - nova fábrica de input `build_promocao_input(...)`
  - `execute_promocao_workflow(...)` agora recebe `workflow_input` explícito
  - `execute_promocao_from_post(...)` ficou como adapter fino (constrói DTO + delega)

## Testes adicionados/ajustados
- `tests/membros/test_application_promotion_workflow.py`
  - mantido teste via adapter (`execute_promocao_from_post`)
  - adicionado teste direto do caso de uso com DTO (`execute_promocao_workflow` + `build_promocao_input`) sem `QueryDict`

## Validação técnica
- `./.venv/Scripts/python.exe manage.py check` -> OK
- `./.venv/Scripts/python.exe -m pytest tests/membros/test_application_promotion_workflow.py -q` -> 3 passed
- `./.venv/Scripts/python.exe -m pytest tests/membros -q` -> 30 passed
- Regressão dirigida plataforma:
  - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q` -> 87 passed
- Smoke funcional registrado em:
  - `docs/etapas/smoke_onda3_membros_promotion_workflow_dto_20260310_170750.md`

## Riscos e trade-offs
- Trade-off: ainda mantemos adapter baseado em `get/getlist` para compatibilidade rápida com Django/HTMX.
- Ganho: núcleo do caso de uso ficou desacoplado da interface HTTP, facilitando evolução para outros adapters.

## Rollback local (sem Git)
1. Remover DTO/fábrica (`PromocaoWorkflowInput`, `build_promocao_input`) do arquivo `promotion_workflow.py`.
2. Restaurar assinatura anterior de `execute_promocao_workflow(...)` com argumentos primitivos.
3. Ajustar testes removendo cenário DTO.
4. Reexecutar:
   - `./.venv/Scripts/python.exe manage.py check`
   - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q`

## Próximo passo recomendado
Aplicar o mesmo padrão de contrato interno explícito para outros fluxos críticos já em extração (ex.: `eventos` e `pagamentos`) para uniformidade arquitetural da Onda 3.

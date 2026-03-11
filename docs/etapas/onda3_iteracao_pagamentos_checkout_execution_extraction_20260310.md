# Onda 3.3 - Iteracao Pagamentos Checkout Execution Extraction

Data: 2026-03-10
Status: concluido

## Objetivo
Extrair a execução do checkout Pix (provider + service + tratamento de `PagamentoProviderError`) para `application`, reduzindo lógica de domínio na view.

## Entregas
- Novo módulo:
  - `apps/backend/app/modules/pagamentos/application/checkout_execution.py`
    - `PixCheckoutExecutionResult`
    - `execute_pix_checkout_payment`
  - Responsabilidades:
    - resolver provider Mercado Pago por organização
    - executar `PagamentoService.iniciar_pagamento`
    - aplicar callback de vínculo com inscrição
    - tratar erro de domínio (`PagamentoProviderError`) em resultado explícito
    - registrar erro inesperado e propagar exceção
- Refactor em `pagamentos/views.py`:
  - `PixCheckoutView.post` delega execução para `execute_pix_checkout_payment`
  - view mantém apenas:
    - tradução de erro para `form.add_error`
    - render/redirect HTTP

## Testes adicionados
- `tests/pagamentos/test_application_checkout_execution.py`
  - sucesso com vínculo de transação
  - falha controlada de provider
  - falha inesperada propagada

## Validação técnica
- `./.venv/Scripts/python.exe manage.py check` -> OK
- `./.venv/Scripts/python.exe -m pytest tests/pagamentos/test_application_checkout_execution.py -q` -> 3 passed
- `./.venv/Scripts/python.exe -m pytest tests/pagamentos -q` -> 16 passed
- Regressão dirigida plataforma:
  - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q` -> 93 passed
- Smoke funcional registrado em:
  - `docs/etapas/smoke_onda3_pagamentos_checkout_execution_20260310_171945.md`

## Riscos e trade-offs
- Trade-off: a view ainda instancia formulário e resolve organização inicial (camada de interface), por escolha incremental.
- Ganho: execução de pagamento ficou isolada e testável sem HTTP.

## Rollback local (sem Git)
1. Remover `apps/backend/app/modules/pagamentos/application/checkout_execution.py`.
2. Restaurar execução inline de `PagamentoService` em `PixCheckoutView.post`.
3. Remover `tests/pagamentos/test_application_checkout_execution.py`.
4. Reexecutar:
   - `./.venv/Scripts/python.exe manage.py check`
   - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q`

## Próximo passo recomendado
Unificar o fluxo completo de checkout em um único use-case (validação de entrada + preparação + execução + vínculo), mantendo `PixCheckoutView` como adapter fino.

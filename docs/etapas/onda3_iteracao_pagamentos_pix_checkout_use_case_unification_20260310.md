# Onda 3.3 - Iteracao Pagamentos Pix Checkout Use Case Unification

Data: 2026-03-10
Status: concluido

## Objetivo
Unificar o fluxo de checkout Pix em um único use-case de `application` (preparação + execução + vínculo), deixando `PixCheckoutView` como adapter HTTP.

## Entregas
- Novo módulo:
  - `apps/backend/app/modules/pagamentos/application/pix_checkout_use_case.py`
    - `PixCheckoutUseCaseResult`
    - `execute_pix_checkout_use_case`
  - Orquestra:
    - `build_pix_checkout_command_input`
    - `prepare_pix_checkout_command`
    - `execute_pix_checkout_payment`
- Refactor em `pagamentos/views.py`:
  - `PixCheckoutView.post` passa a chamar apenas `execute_pix_checkout_use_case`
  - mantém tratamento de form inválido e render/redirect HTTP

## Testes adicionados
- `tests/pagamentos/test_application_pix_checkout_use_case.py`
  - caminho de sucesso
  - erro de provider retornando falha controlada

## Validação técnica
- `./.venv/Scripts/python.exe manage.py check` -> OK
- `./.venv/Scripts/python.exe -m pytest tests/pagamentos/test_application_pix_checkout_use_case.py -q` -> 2 passed
- `./.venv/Scripts/python.exe -m pytest tests/pagamentos -q` -> 18 passed
- Regressão dirigida plataforma:
  - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q` -> 95 passed
- Smoke funcional registrado em:
  - `docs/etapas/smoke_onda3_pagamentos_pix_checkout_use_case_20260310_172420.md`

## Riscos e trade-offs
- Trade-off: o use-case ainda recebe `cleaned_data` de formulário Django para acelerar migração incremental.
- Ganho: orquestração centralizada e testável sem HTTP, reduzindo complexidade da view.

## Rollback local (sem Git)
1. Remover `apps/backend/app/modules/pagamentos/application/pix_checkout_use_case.py`.
2. Restaurar no `PixCheckoutView.post` a orquestração direta entre workflow + execution.
3. Remover `tests/pagamentos/test_application_pix_checkout_use_case.py`.
4. Reexecutar:
   - `./.venv/Scripts/python.exe manage.py check`
   - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q`

## Próximo passo recomendado
Aplicar o mesmo padrão unificado no fluxo de `FaturamentoView.post` para consistência de contratos internos de checkout em `pagamentos`.

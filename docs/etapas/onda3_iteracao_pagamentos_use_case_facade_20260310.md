# Onda 3.3 - Iteracao Pagamentos Use Case Facade

Data: 2026-03-10
Status: concluido

## Objetivo
Consolidar uma fachada única de casos de uso de `pagamentos` para padronizar imports e contratos da camada de aplicação.

## Entregas
- Nova fachada:
  - `apps/backend/app/modules/pagamentos/application/use_cases.py`
  - agrega exports de:
    - checkout pix (`execute_pix_checkout_use_case`)
    - checkout faturamento (`build_faturamento_checkout_input`, `execute_faturamento_checkout_use_case`)
    - resolução de organização (`obter_organizacao_checkout`, `obter_organizacao_webhook`)
    - helpers de transação (`mapear_status_pagamento`, `normalizar_uuid`)
- Atualização de pacote:
  - `apps/backend/app/modules/pagamentos/application/__init__.py` com `__all__` explícito
- Refactor em `pagamentos/views.py`:
  - imports de aplicação passam a vir da fachada única `application.use_cases`

## Testes adicionados
- `tests/pagamentos/test_application_use_cases_facade.py`
  - valida símbolos exportados na fachada
  - valida reuso funcional dos helpers de transação via fachada

## Validação técnica
- `./.venv/Scripts/python.exe manage.py check` -> OK
- `./.venv/Scripts/python.exe -m pytest tests/pagamentos/test_application_use_cases_facade.py -q` -> 2 passed
- `./.venv/Scripts/python.exe -m pytest tests/pagamentos -q` -> 23 passed
- Regressão dirigida plataforma:
  - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q` -> 100 passed
- Smoke funcional registrado em:
  - `docs/etapas/smoke_onda3_pagamentos_use_case_facade_20260310_173157.md`

## Riscos e trade-offs
- Trade-off: a fachada expõe funções de múltiplos subfluxos no mesmo módulo para privilegiar consistência operacional da Onda 3.3.
- Ganho: padronização de ponto de entrada da camada `application`, reduzindo acoplamento de views com módulos internos específicos.

## Rollback local (sem Git)
1. Remover `apps/backend/app/modules/pagamentos/application/use_cases.py`.
2. Reverter imports de `pagamentos/views.py` para módulos específicos anteriores.
3. Reverter `apps/backend/app/modules/pagamentos/application/__init__.py`.
4. Remover `tests/pagamentos/test_application_use_cases_facade.py`.
5. Reexecutar:
   - `./.venv/Scripts/python.exe manage.py check`
   - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q`

## Próximo passo recomendado
Iniciar fechamento da Onda 3 com hardening: checklist de contratos, cobertura mínima por fluxo crítico e estabilização de warnings pendentes não bloqueantes.

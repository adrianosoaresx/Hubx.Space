# Onda 3.3 - Iteracao Pagamentos Faturamento Use Case Unification

Data: 2026-03-10
Status: concluido

## Objetivo
Aplicar no faturamento o mesmo padrão de use-case unificado adotado no checkout Pix, mantendo a view como adapter HTTP.

## Entregas
- Novo módulo:
  - `apps/backend/app/modules/pagamentos/application/faturamento_checkout_use_case.py`
    - `FaturamentoCheckoutInput`
    - `FaturamentoCheckoutResult`
    - `build_faturamento_checkout_input`
    - `execute_faturamento_checkout_use_case`
  - Responsabilidades:
    - normalização de input de faturamento
    - execução do registro via callback
    - composição de erro de domínio
    - construção da URL de retorno com status e mensagem
- Refactor em `pagamentos/views.py`:
  - `FaturamentoView.post` passa a delegar para `execute_faturamento_checkout_use_case`
  - view mantém validação de form e render/redirect HTTP

## Testes adicionados
- `tests/pagamentos/test_application_faturamento_checkout_use_case.py`
  - normalização de input
  - fluxo de sucesso com URL de retorno
  - fluxo de erro quando inscrição não é localizada

## Validação técnica
- `./.venv/Scripts/python.exe manage.py check` -> OK
- `./.venv/Scripts/python.exe -m pytest tests/pagamentos/test_application_faturamento_checkout_use_case.py -q` -> 3 passed
- `./.venv/Scripts/python.exe -m pytest tests/pagamentos -q` -> 21 passed
- Regressão dirigida plataforma:
  - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q` -> 98 passed
- Smoke funcional registrado em:
  - `docs/etapas/smoke_onda3_pagamentos_faturamento_use_case_20260310_172815.md`

## Riscos e trade-offs
- Trade-off: o callback de registro ainda depende do contexto HTTP/request para autorização de usuário, mantendo compatibilidade incremental.
- Ganho: fluxo de faturamento agora está centralizado e testável sem acoplamento direto à view.

## Rollback local (sem Git)
1. Remover `apps/backend/app/modules/pagamentos/application/faturamento_checkout_use_case.py`.
2. Restaurar lógica inline do `FaturamentoView.post` em `pagamentos/views.py`.
3. Remover `tests/pagamentos/test_application_faturamento_checkout_use_case.py`.
4. Reexecutar:
   - `./.venv/Scripts/python.exe manage.py check`
   - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q`

## Próximo passo recomendado
Padronizar o módulo `pagamentos` em uma fachada única de casos de uso (`checkout_pix`, `checkout_faturamento`, `status`, `retorno`) para fechar Onda 3.3 com contrato de aplicação consistente.

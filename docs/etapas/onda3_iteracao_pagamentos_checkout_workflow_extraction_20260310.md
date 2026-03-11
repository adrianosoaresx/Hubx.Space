# Onda 3.3 - Iteracao Pagamentos Checkout Workflow Extraction

Data: 2026-03-10
Status: concluido

## Objetivo
Extrair a preparação do checkout Pix (`PixCheckoutView.post`) para a camada `application`, com contrato interno explícito e view mais enxuta.

## Entregas
- Novo módulo:
  - `apps/backend/app/modules/pagamentos/application/checkout_workflow.py`
    - `PixCheckoutCommandInput`
    - `PixCheckoutCommandResult`
    - `build_pix_checkout_command_input`
    - `prepare_pix_checkout_command`
  - Responsabilidades:
    - normalização do payload de checkout
    - resolução de organização alvo
    - criação de `Pedido`
    - composição de `dados_pagamento` por método (pix/cartao/boleto)
- Refactor em `pagamentos/views.py`:
  - `PixCheckoutView.post` delega preparação para o workflow de `application`
  - mantém renderização/form handling no adapter HTTP

## Testes adicionados
- `tests/pagamentos/test_application_checkout_workflow.py`
  - normalização de input
  - resolução de organização + payload pix
  - defaults do cartão (`parcelas=1`)

## Validação técnica
- `./.venv/Scripts/python.exe manage.py check` -> OK
- `./.venv/Scripts/python.exe -m pytest tests/pagamentos/test_application_checkout_workflow.py -q` -> 3 passed
- `./.venv/Scripts/python.exe -m pytest tests/pagamentos -q` -> 13 passed
- Regressão dirigida plataforma:
  - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q` -> 90 passed
- Smoke funcional registrado em:
  - `docs/etapas/smoke_onda3_pagamentos_checkout_workflow_20260310_171515.md`

## Riscos e trade-offs
- Trade-off: a execução do provider (`PagamentoService`) permanece na view para manter superfície de erro HTTP inalterada nesta fatia.
- Risco residual: `checkout` ainda depende de integrações externas no mesmo endpoint; próxima fatia pode extrair orquestração completa com política de erros.

## Rollback local (sem Git)
1. Remover `apps/backend/app/modules/pagamentos/application/checkout_workflow.py`.
2. Restaurar criação de pedido/composição de payload inline em `pagamentos/views.py`.
3. Remover `tests/pagamentos/test_application_checkout_workflow.py`.
4. Reexecutar:
   - `./.venv/Scripts/python.exe manage.py check`
   - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q`

## Próximo passo recomendado
Extrair a orquestração de execução de pagamento (provider/service + tratamento de exceções de domínio) para `application`, mantendo a view somente como tradução HTTP.

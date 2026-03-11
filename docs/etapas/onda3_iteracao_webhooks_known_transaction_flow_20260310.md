# Onda 3.1 - Iteracao Webhooks Known Transaction Flow

Data: 2026-03-10
Status: concluido

## Objetivo
Reduzir acoplamento da etapa de transacao conhecida no webhook, movendo lookup/processamento para `application` e validando fluxo de confirmacao por smoke controlado.

## Entregas
- Novo modulo application:
  - `apps/backend/app/modules/webhooks/application/payment_webhook_processing.py`
    - `find_transaction_by_external_id`
    - `build_provider_for_webhook`
    - `confirm_known_transaction`
    - `atualizar_inscricao_transacao_aprovada`
- Refactor em `pagamentos/views.py` (`WebhookView`):
  - lookup de transacao delegada para `find_transaction_by_external_id`
  - montagem de provider + confirmacao delegadas para `confirm_known_transaction`
  - sincronizacao de inscricao delegada para `atualizar_inscricao_transacao_aprovada`

## Testes adicionados
- `tests/webhooks/test_application_payment_webhook_processing.py`
  - cobertura de lookup, provider factory, callback de confirmacao e regra de sincronizacao de inscricao.
- `tests/pagamentos/test_webhook_views_known_transaction.py`
  - integra endpoint Mercado Pago com transacao conhecida e confirmacao stubada.

## Validacao tecnica
- `./.venv/Scripts/python.exe manage.py check` -> OK
- `./.venv/Scripts/python.exe -m pytest tests/webhooks/test_application_payment_webhook_flow.py tests/webhooks/test_application_payment_webhook_processing.py tests/pagamentos/test_webhook_views_known_transaction.py -q` -> 19 passed
- Smoke funcional registrado em:
  - `docs/etapas/smoke_onda3_webhooks_known_transaction_flow_20260310_154609.md`

## Riscos e trade-offs
- Trade-off: smoke de transacao conhecida usa stub de confirmacao para manter execucao local deterministica sem tokens reais de provider.
- Risco residual: confirmacao real com provider externo continua dependente de credenciais/ambiente e deve ser validada em onda de integracoes.

## Rollback local (sem Git)
1. Remover `apps/backend/app/modules/webhooks/application/payment_webhook_processing.py`.
2. Reverter `pagamentos/views.py` para lookup/confirmacao/sincronizacao inline.
3. Remover testes:
   - `tests/webhooks/test_application_payment_webhook_processing.py`
   - `tests/pagamentos/test_webhook_views_known_transaction.py`
4. Reexecutar validacao minima:
   - `./.venv/Scripts/python.exe manage.py check`
   - `./.venv/Scripts/python.exe -m pytest tests/pagamentos tests/webhooks -q`

## Proximo passo recomendado
Avancar para `notificacoes` (Onda 3.1) com extracao de regras de montagem de payload/template e smoke por usuario de negocio em organizacao valida.

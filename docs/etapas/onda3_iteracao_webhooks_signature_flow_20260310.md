# Onda 3.1 - Iteracao Webhooks Signature Flow

Data: 2026-03-10
Status: concluido

## Objetivo
Extrair regras de parse/identificacao/assinatura do webhook para camada `application` e reduzir acoplamento em `pagamentos/views.py`, mantendo contrato REST atual.

## Entregas
- Novo modulo application:
  - `apps/backend/app/modules/webhooks/application/payment_webhook_flow.py`
    - `parse_webhook_payload`
    - `extract_external_id`
    - `resolve_signature_secret`
    - `validate_hmac_signature`
- Refactor em `pagamentos/views.py`:
  - `WebhookView` e `PayPalWebhookView` agora delegam parse/extracao/validacao de assinatura para `application`.
  - Comportamento funcional preservado:
    - sem id: `400`
    - assinatura invalida: `403`
    - transacao desconhecida com assinatura valida: `200`
- Testes adicionados:
  - `tests/webhooks/test_application_payment_webhook_flow.py` (10 cenarios)

## Validacao tecnica
- `./.venv/Scripts/python.exe manage.py check` -> OK
- `./.venv/Scripts/python.exe -m pytest tests/pagamentos tests/webhooks -q` -> 19 passed
- Smoke funcional registrado em:
  - `docs/etapas/smoke_onda3_webhooks_signature_flow_20260310_153932.md`

## Riscos e trade-offs
- Trade-off: extracao focada em assinatura/payload sem mover confirmacao de pagamento para evitar regressao em provider runtime nesta fatia.
- Risco residual: cenarios com transacao existente + confirmacao provider continuam em view/mixin e dependem de smoke com sandbox de provider.

## Rollback local (sem Git)
1. Remover arquivo `apps/backend/app/modules/webhooks/application/payment_webhook_flow.py`.
2. Reverter delegacoes em `pagamentos/views.py` para implementacao inline anterior (`_parse_body` + `_assinatura_valida`).
3. Remover `tests/webhooks/test_application_payment_webhook_flow.py`.
4. Reexecutar:
   - `./.venv/Scripts/python.exe manage.py check`
   - `./.venv/Scripts/python.exe -m pytest tests/pagamentos -q`

## Proximo passo recomendado
Extrair fluxo de confirmacao/roteamento de webhook com transacao conhecida (incluindo politica de retry) para `application`, com testes de integracao controlando provider por stub.

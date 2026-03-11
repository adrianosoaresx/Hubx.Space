# Smoke Onda 3.1 - Webhooks Signature Flow

Data: 2026-03-10 15:39:32
Usuario de negocio: id=3 username=daianygaspar email=daianygaspar@gmail.com user_type=nucleado organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Escopo: validacao de assinatura (Mercado Pago/PayPal) e parse de payload sem transacao conhecida.

| Check | Path | Status | Observacao |
|---|---|---:|---|
| perfil_negocio | `/accounts/perfil/` | 200 | Usuario autenticado e com organizacao valida |
| mp_missing_id | `/pagamentos/webhook/mercadopago/` | 400 | `missing id` |
| mp_unknown_signed | `/pagamentos/webhook/mercadopago/` | 200 | Assinatura valida e transacao desconhecida |
| mp_invalid_signature | `/pagamentos/webhook/mercadopago/` | 403 | Assinatura invalida bloqueada |
| pp_unknown_signed | `/pagamentos/webhook/paypal/` | 200 | Assinatura valida e transacao desconhecida |
| pp_invalid_signature | `/pagamentos/webhook/paypal/` | 403 | Assinatura invalida bloqueada |

Comando executado:
- `./.venv/Scripts/python.exe manage.py shell -c "... smoke webhook controlado ..."`

Notas:
- Logs esperados observados para cenarios negativos: `webhook_sem_id` e `webhook_assinatura_invalida`.
- Sem mutacao de dados de negocio neste smoke (nenhuma transacao existente foi confirmada).

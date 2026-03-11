# Smoke Onda 3.1 - Webhooks Known Transaction Flow

Data: 2026-03-10 15:46:09
Usuario de negocio: id=3 username=daianygaspar email=daianygaspar@gmail.com user_type=nucleado organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Escopo: webhook com transacao conhecida + confirmacao controlada (stub local) + validacao de assinatura.

Transacoes criadas para smoke:
- Mercado Pago: id=44 external_id=known-smoke-mp-001
- PayPal: id=45 external_id=known-smoke-pp-001

| Check | Path | Status | Observacao |
|---|---|---:|---|
| perfil_negocio | `/accounts/perfil/` | 200 | Usuario autenticado com organizacao valida |
| mp_known_signed | `/pagamentos/webhook/mercadopago/` | 200 | Transacao conhecida confirmada via stub (`approved`) |
| mp_known_invalid_signature | `/pagamentos/webhook/mercadopago/` | 403 | Assinatura invalida bloqueada |
| pp_known_signed | `/pagamentos/webhook/paypal/` | 200 | Transacao conhecida confirmada via stub (`approved`) |
| pp_known_invalid_signature | `/pagamentos/webhook/paypal/` | 403 | Assinatura invalida bloqueada |

Comando executado:
- `./.venv/Scripts/python.exe manage.py shell` com script inline (sequencia controlada)

Notas:
- Confirmacao de pagamento foi stubada localmente para evitar dependencia externa de provider.
- Logs esperados em cenarios negativos: `webhook_assinatura_invalida`.

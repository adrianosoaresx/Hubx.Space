# Smoke Onda 2 - Eventos Orcamento e Listagem por Dia

Data: 2026-03-10 14:19:08
Usuario: id=2 username=cdladmin email=cdladmin@hubx.local user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Evento usado: id=85c9a012-7e6e-49dc-8ce0-68081eba9f86 dia=2026-02-20

| Check | Path | Status | Redirect/Obs |
|---|---|---:|---|
| perfil | `/accounts/perfil/` | 200 | `` |
| eventos_painel | `/eventos/` | 200 | `` |
| eventos_por_dia | `/eventos/eventos_por_dia/?dia=2026-02-20` | 200 | `` |
| checkout_pix | `/pagamentos/checkout/pix/` | 200 | `` |
| evento_orcamento_post | `/eventos/api/eventos/85c9a012-7e6e-49dc-8ce0-68081eba9f86/orcamento/` | 200 | `{"status":"ok","alteracoes":{...}}` |

Payload POST aplicado em `evento_orcamento_post`:
- `orcamento_estimado=123.45`
- `valor_gasto=67.89`

# Smoke Onda 2 - Pagamentos e Eventos

Data: 2026-03-10 13:51:29
Usuario: id=2 username=cdladmin email=cdladmin@hubx.local user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc

| Check | Path | Status | Redirect/Obs |
|---|---|---:|---|
| perfil | /accounts/perfil/ | 200 | ` |
| eventos_lista | /eventos/ | 200 | ` |
| eventos_calendario_ultimos30 | /eventos/ultimos-30/ | 200 | ` |
| pagamentos_checkout_pix | /pagamentos/checkout/pix/ | 200 | ` |
| pagamentos_faturamento | /pagamentos/checkout/faturamento/ | 200 | ` |
| tokens_convites | /tokens/convites/ | 200 | ` |

Observacao: no primeiro disparo do smoke desta iteracao, a rota /eventos/calendario/ retornou 404 (rota inexistente). O check foi corrigido para a rota valida /eventos/ultimos-30/.

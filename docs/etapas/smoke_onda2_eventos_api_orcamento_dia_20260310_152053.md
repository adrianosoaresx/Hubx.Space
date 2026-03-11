# Smoke Onda 2 - Eventos API Orcamento e Dia

Data: 2026-03-10 15:20:53
Usuario: id=2 username=cdladmin email=cdladmin@hubx.local user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Evento alvo: id=85c9a012-7e6e-49dc-8ce0-68081eba9f86 slug=qqqqqqqqqqqq dia=2026-02-20
Orcamento inicial/final: 123.45 -> 123.45
Valor gasto inicial/final: 67.89 -> 67.89

| Check | Path | Status | Redirect/Obs |
|---|---|---:|---|
| perfil | `/accounts/perfil/` | 200 | `` |
| eventos_painel | `/eventos/` | 200 | `` |
| evento_orcamento_post_apply | `/eventos/api/eventos/85c9a012-7e6e-49dc-8ce0-68081eba9f86/orcamento/` | 200 | `{"status":"ok","alteracoes":{"orcamento_estimado":{"antes":"123.45","depois":"124.45"},"valor_gasto":{"antes":"67.89","depois":"68.89"}}}` |
| eventos_por_dia_get | `/eventos/eventos_por_dia/?dia=2026-02-20` | 200 | `` |
| evento_orcamento_post_rollback | `/eventos/api/eventos/85c9a012-7e6e-49dc-8ce0-68081eba9f86/orcamento/` | 200 | `{"status":"ok","alteracoes":{"orcamento_estimado":{"antes":"124.45","depois":"123.45"},"valor_gasto":{"antes":"68.89","depois":"67.89"}}}` |

## Observacao de rollback controlado
- O smoke executou POST de aplicacao e POST de rollback em sequencia para garantir ausencia de efeito residual de dados.

# Smoke Onda 2 - Eventos Convites Publicos

Data: 2026-03-10 14:14:55
Usuario: id=2 username=cdladmin email=cdladmin@hubx.local user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Convite utilizado: evento_id=85c9a012-7e6e-49dc-8ce0-68081eba9f86 short_code=zj8M4nhwiV

| Check | Path | Status | Redirect/Obs |
|---|---|---:|---|
| perfil | /accounts/perfil/ | 200 | ` |
| eventos_painel | /eventos/ | 200 | ` |
| tokens_convites | /tokens/convites/ | 200 | ` |
| convite_publico | /eventos/c/zj8M4nhwiV/ | 200 | ` |
| checkout_pix | /pagamentos/checkout/pix/ | 200 | ` |

Observacao: antes da correcao, convite_publico quebrava com TemplateSyntaxError por falta de {% load static %} em ventos/templates/eventos/convites/public.html.

# Smoke Onda 2 - Eventos Portfolio Context

Data: 2026-03-10 15:28:34
Usuario: id=2 username=cdladmin email=cdladmin@hubx.local user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Evento base sem midia: id=85c9a012-7e6e-49dc-8ce0-68081eba9f86 slug=qqqqqqqqqqqq
Evento com midia: id=7b720863-2fa3-4423-8e29-f75b6f13a80a slug=mulher-empreendedora-2
Midia alvo: id=2

| Check | Path | Status | Redirect/Obs |
|---|---|---:|---|
| perfil | `/accounts/perfil/` | 200 | `` |
| evento_detalhe_base | `/eventos/evento/85c9a012-7e6e-49dc-8ce0-68081eba9f86/` | 200 | `` |
| evento_detalhe_portfolio_add | `/eventos/evento/85c9a012-7e6e-49dc-8ce0-68081eba9f86/?portfolio_adicionar=1` | 200 | `` |
| evento_detalhe_portfolio_filter | `/eventos/evento/85c9a012-7e6e-49dc-8ce0-68081eba9f86/?q=evento` | 200 | `` |
| evento_detalhe_base_com_midia | `/eventos/evento/7b720863-2fa3-4423-8e29-f75b6f13a80a/` | 200 | `` |
| evento_detalhe_portfolio_media | `/eventos/evento/7b720863-2fa3-4423-8e29-f75b6f13a80a/?portfolio_midia=2&q=evento` | 200 | `` |
| evento_portfolio_edit_get | `/eventos/evento/portfolio/2/editar/` | 200 | `` |

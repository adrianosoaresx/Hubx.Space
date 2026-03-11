# Smoke Onda 2 - Eventos Briefing Flow

Data: 2026-03-10 14:33:01
Usuario: id=2 username=cdladmin email=cdladmin@hubx.local user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Evento briefing: id=85c9a012-7e6e-49dc-8ce0-68081eba9f86 slug=qqqqqqqqqqqq
Template briefing: id=1 nome=briefing modelo 1
Briefing persistido: id=2 template_id=1

| Check | Path | Status | Redirect/Obs |
|---|---|---:|---|
| perfil | `/accounts/perfil/` | 200 | `` |
| eventos_painel | `/eventos/` | 200 | `` |
| evento_detalhe | `/eventos/evento/85c9a012-7e6e-49dc-8ce0-68081eba9f86/` | 200 | `` |
| briefing_selecionar_get | `/eventos/eventos/85c9a012-7e6e-49dc-8ce0-68081eba9f86/briefing/selecionar/` | 200 | `` |
| briefing_selecionar_post | `/eventos/eventos/85c9a012-7e6e-49dc-8ce0-68081eba9f86/briefing/selecionar/` | 302 | `/eventos/eventos/85c9a012-7e6e-49dc-8ce0-68081eba9f86/briefing/preencher/` |
| briefing_preencher_get | `/eventos/eventos/85c9a012-7e6e-49dc-8ce0-68081eba9f86/briefing/preencher/` | 200 | `` |
| briefing_visualizar_get | `/eventos/eventos/85c9a012-7e6e-49dc-8ce0-68081eba9f86/briefing/visualizar/` | 200 | `` |

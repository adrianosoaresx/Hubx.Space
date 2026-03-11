# Smoke Onda 2 - Eventos Event Write Policy

Data: 2026-03-10 14:38:55
Usuario: id=2 username=cdladmin email=cdladmin@hubx.local user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Evento alvo: id=85c9a012-7e6e-49dc-8ce0-68081eba9f86 slug=qqqqqqqqqqqq

| Check | Path | Status | Redirect/Obs |
|---|---|---:|---|
| perfil | `/accounts/perfil/` | 200 | `` |
| eventos_painel | `/eventos/` | 200 | `` |
| evento_novo_get | `/eventos/evento/novo/` | 200 | `` |
| evento_editar_get | `/eventos/evento/85c9a012-7e6e-49dc-8ce0-68081eba9f86/editar/` | 200 | `` |
| evento_excluir_get | `/eventos/evento/85c9a012-7e6e-49dc-8ce0-68081eba9f86/excluir/` | 200 | `` |
| evento_excluir_modal_htmx_get | `/eventos/evento/85c9a012-7e6e-49dc-8ce0-68081eba9f86/excluir/` | 200 | `` |

## Achados durante o smoke
- Fluxo inicialmente falhou por `TemplateSyntaxError` em templates com uso de `{% static %}` sem `{% load static %}`.
- Correcoes aplicadas:
  - `eventos/templates/eventos/partials/eventos/_form_fields.html`
  - `eventos/templates/eventos/partials/evento_delete_modal.html`
- Reexecucao apos correcoes: smoke 100% OK.

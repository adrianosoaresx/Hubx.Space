# Smoke Onda 2 - Eventos Inscricao Management

Data: 2026-03-10 14:45:12
Usuario: id=2 username=cdladmin email=cdladmin@hubx.local user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Inscricao alvo: uuid=f2de5908-f5f7-49c3-ac34-fc7a13a75677 id=12 evento_id=7b720863-2fa3-4423-8e29-f75b6f13a80a
Pagamento validado: inicial=True apos_post_1=False final=True

| Check | Path | Status | Redirect/Obs |
|---|---|---:|---|
| perfil | `/accounts/perfil/` | 200 | `` |
| eventos_painel | `/eventos/` | 200 | `` |
| evento_detalhe | `/eventos/evento/7b720863-2fa3-4423-8e29-f75b6f13a80a/` | 200 | `` |
| inscricao_editar_get | `/eventos/inscricoes/f2de5908-f5f7-49c3-ac34-fc7a13a75677/editar/` | 200 | `` |
| inscricao_toggle_validacao_post_1 | `/eventos/inscricoes/f2de5908-f5f7-49c3-ac34-fc7a13a75677/validacao/` | 302 | `/eventos/evento/7b720863-2fa3-4423-8e29-f75b6f13a80a/` |
| inscricao_toggle_validacao_post_2 | `/eventos/inscricoes/f2de5908-f5f7-49c3-ac34-fc7a13a75677/validacao/` | 302 | `/eventos/evento/7b720863-2fa3-4423-8e29-f75b6f13a80a/` |

## Achados durante o smoke
- O fluxo inicialmente falhou por `TemplateSyntaxError` em templates de inscricao com uso de `{% static %}` sem `{% load static %}`.
- Correcoes aplicadas:
  - `eventos/templates/eventos/inscricoes/inscricao_form.html`
  - `eventos/templates/eventos/inscricoes/_metodo_pagamento_cards.html`
- Reexecucao apos correcoes: smoke 100% OK.

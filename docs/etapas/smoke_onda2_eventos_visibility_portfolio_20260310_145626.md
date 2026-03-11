# Smoke Onda 2 - Eventos Visibility Portfolio

Data: 2026-03-10 14:56:26
Usuario: id=2 username=cdladmin email=cdladmin@hubx.local user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Evento alvo portfolio/inscricao: id=7b720863-2fa3-4423-8e29-f75b6f13a80a
Midia alvo: id=2
Inscricao alvo: uuid=f2de5908-f5f7-49c3-ac34-fc7a13a75677

| Check | Path | Status | Redirect/Obs |
|---|---|---:|---|
| evento_portfolio_edit_get | `/eventos/evento/portfolio/2/editar/` | 200 | `` |
| evento_portfolio_delete_get | `/eventos/evento/portfolio/2/excluir/` | 200 | `` |
| inscricao_checkout_get | `/eventos/inscricoes/f2de5908-f5f7-49c3-ac34-fc7a13a75677/checkout/` | 200 | `` |
| inscricao_resultado_get | `/eventos/inscricoes/f2de5908-f5f7-49c3-ac34-fc7a13a75677/resultado/` | 200 | `` |

## Achados durante o smoke
- O fluxo de portfolio inicialmente falhou por `VariableDoesNotExist` com `request.META.HTTP_REFERER` ausente no contexto do template.
- Correcoes aplicadas:
  - `eventos/templates/eventos/portfolio/form.html`
  - `eventos/templates/eventos/portfolio/confirm_delete.html`
- Reexecucao apos correcoes: smoke 100% OK.

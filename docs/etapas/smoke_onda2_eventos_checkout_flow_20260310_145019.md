# Smoke Onda 2 - Eventos Checkout Flow

Data: 2026-03-10 14:50:19
Usuario: id=2 username=cdladmin email=cdladmin@hubx.local user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Inscricao alvo: uuid=f2de5908-f5f7-49c3-ac34-fc7a13a75677 id=12 evento_id=7b720863-2fa3-4423-8e29-f75b6f13a80a
Estado inscricao: metodo_inicial=None metodo_final=None validado_inicial=True validado_final=True valor_inicial=None valor_final=None

| Check | Path | Status | Redirect/Obs |
|---|---|---:|---|
| perfil | `/accounts/perfil/` | 200 | `` |
| eventos_painel | `/eventos/` | 200 | `` |
| evento_detalhe | `/eventos/evento/7b720863-2fa3-4423-8e29-f75b6f13a80a/` | 200 | `` |
| checkout_get | `/eventos/inscricoes/f2de5908-f5f7-49c3-ac34-fc7a13a75677/checkout/` | 200 | `` |
| checkout_post | `/eventos/inscricoes/f2de5908-f5f7-49c3-ac34-fc7a13a75677/checkout/` | 302 | `/eventos/inscricoes/f2de5908-f5f7-49c3-ac34-fc7a13a75677/checkout/` |
| resultado_get | `/eventos/inscricoes/f2de5908-f5f7-49c3-ac34-fc7a13a75677/resultado/` | 200 | `` |

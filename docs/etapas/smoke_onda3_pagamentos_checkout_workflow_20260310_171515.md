# Smoke Onda 3.3 - Pagamentos Checkout Workflow

Data: 2026-03-10 17:15:15
Usuario de negocio (admin): id=2 username=cdladmin user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Evento base: id=65db8188-5715-4a8b-ac54-0a002e978c20 slug=evento-para-testes organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Inscricao alvo: uuid=febff482-c6d4-4c7d-ada0-6dd9ac25b60f user_id=2 evento_id=65db8188-5715-4a8b-ac54-0a002e978c20
Escopo: validar extração do fluxo de preparação do checkout Pix para `application`.

| Check | Path | Status | Observacao |
|---|---|---:|---|
| pagamentos_pix_checkout_get | `/pagamentos/checkout/pix/` | 200 | Formulário de checkout carregado |
| pagamentos_pix_checkout_post | `/pagamentos/checkout/pix/` | 302 | Redireciona para resultado de checkout |
| pagamentos_pix_checkout_redirect | `/pagamentos/checkout/resultado/46/` | OK | Rota de resultado gerada corretamente |
| pagamentos_transacao_criada | `Transacao(id=46)` | OK | `status=approved`, `metodo=pix`, `pedido.organizacao` preservada |
| pagamentos_inscricao_vinculada | `InscricaoEvento(uuid=febff482-c6d4-4c7d-ada0-6dd9ac25b60f)` | OK | `metodo_pagamento=pix`, `pagamento_validado=True` |

Comando executado:
- `./.venv/Scripts/python.exe manage.py shell -c "<script smoke checkout workflow>"`

Observacao operacional:
- O smoke utilizou stub local de `PagamentoService.iniciar_pagamento` para evitar dependência externa de provider e validar apenas o fluxo interno da aplicação.

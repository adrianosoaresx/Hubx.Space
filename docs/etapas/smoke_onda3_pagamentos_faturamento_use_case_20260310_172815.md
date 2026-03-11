# Smoke Onda 3.3 - Pagamentos Faturamento Use Case

Data: 2026-03-10 17:28:15
Usuario de negocio (admin): id=2 username=cdladmin user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Evento base: id=65db8188-5715-4a8b-ac54-0a002e978c20 slug=evento-para-testes organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Inscricao alvo: uuid=febff482-c6d4-4c7d-ada0-6dd9ac25b60f user_id=2 evento_id=65db8188-5715-4a8b-ac54-0a002e978c20
Escopo: validar unificação do fluxo de faturamento em use-case de `application`.

| Check | Path | Status | Observacao |
|---|---|---:|---|
| pagamentos_faturamento_get | `/pagamentos/checkout/faturamento/` | 200 | Formulário de faturamento carregado |
| pagamentos_faturamento_post | `/pagamentos/checkout/faturamento/` | 302 | Redireciona para resultado da inscrição |
| pagamentos_faturamento_redirect | `/eventos/inscricoes/febff482-c6d4-4c7d-ada0-6dd9ac25b60f/resultado/?status=info&message=...` | OK | Mensagem de faturamento preservada |
| pagamentos_faturamento_inscricao_metodo | `InscricaoEvento(uuid=febff482-c6d4-4c7d-ada0-6dd9ac25b60f)` | OK | `metodo_pagamento=faturamento`, `condicao_faturamento=2x` |
| pagamentos_faturamento_inscricao_estado | `InscricaoEvento(uuid=febff482-c6d4-4c7d-ada0-6dd9ac25b60f)` | OK | `transacao=None`, `pagamento_validado=False` |

Comando executado:
- `./.venv/Scripts/python.exe manage.py shell -c "<script smoke faturamento use case>"`

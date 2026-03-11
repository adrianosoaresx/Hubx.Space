# Smoke Onda 3.3 - Pagamentos Use Case Facade

Data: 2026-03-10 17:31:57
Usuario de negocio (admin): id=2 username=cdladmin user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Evento base: id=65db8188-5715-4a8b-ac54-0a002e978c20 slug=evento-para-testes organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Inscricao alvo: uuid=febff482-c6d4-4c7d-ada0-6dd9ac25b60f user_id=2 evento_id=65db8188-5715-4a8b-ac54-0a002e978c20
Escopo: validar fachada única de casos de uso de `pagamentos` aplicada nas views.

| Check | Path | Status | Observacao |
|---|---|---:|---|
| pagamentos_pix_get | `/pagamentos/checkout/pix/` | 200 | Formulário Pix carregado |
| pagamentos_pix_post | `/pagamentos/checkout/pix/` | 302 | Redirect para resultado Pix preservado |
| pagamentos_faturamento_get | `/pagamentos/checkout/faturamento/` | 200 | Formulário Faturamento carregado |
| pagamentos_faturamento_post | `/pagamentos/checkout/faturamento/` | 302 | Redirect para resultado da inscrição preservado |
| pagamentos_transacao_pix | `Transacao(id=49)` | OK | `status=approved`, `metodo=pix`, org preservada |
| pagamentos_inscricao_faturamento | `InscricaoEvento(uuid=febff482-c6d4-4c7d-ada0-6dd9ac25b60f)` | OK | `metodo_pagamento=faturamento`, `condicao_faturamento=2x`, `pagamento_validado=False` |

Comando executado:
- `./.venv/Scripts/python.exe manage.py shell -c "<script smoke use case facade>"`

Observacao operacional:
- O trecho Pix do smoke usou stub local de `PagamentoService.iniciar_pagamento` para eliminar dependência externa e validar fluxo interno da fachada.

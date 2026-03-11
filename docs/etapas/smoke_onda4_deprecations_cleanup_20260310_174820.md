# Smoke Onda 4 - Deprecations Cleanup

Data: 2026-03-10 17:48:20
Usuario de negocio (admin): id=2 username=cdladmin user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Escopo: validar endpoints-chave após limpeza de depreciações Django 6.0.

| Check | Path | Status | Observacao |
|---|---|---:|---|
| conexoes_sections_get | `/conexoes/perfil/sections/conexoes/` | 200 | Página de conexões estável |
| pagamentos_pix_get | `/pagamentos/checkout/pix/` | 200 | Checkout Pix disponível |
| pagamentos_faturamento_get | `/pagamentos/checkout/faturamento/` | 200 | Checkout Faturamento disponível |

Comando executado:
- `./.venv/Scripts/python.exe manage.py shell -c "<script smoke onda4 deprecations>"`

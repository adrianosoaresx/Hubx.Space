# Smoke Etapa 2 - Baseline Script Sequencial

Data: 2026-03-10 17:54:59
Escopo: validar execução ponta-a-ponta do script único de baseline local da Etapa 2.

Script executado:
- `powershell -ExecutionPolicy Bypass -File scripts/smoke_etapa2_baseline.ps1`

Sequência validada:
1. `manage.py check`
2. Regressão dirigida:
   - `pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q`
3. Smoke HTTP local:
   - `/conexoes/perfil/sections/conexoes/`
   - `/pagamentos/checkout/pix/`
   - `/pagamentos/checkout/faturamento/`

Resultado:
- Status final do script: `sucesso`
- Resultado da regressão no script: `100 passed`

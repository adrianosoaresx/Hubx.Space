# Smoke Etapa 2 - Baseline Script com POST Controlado

Data: 2026-03-10 18:01:49
Escopo: validar baseline sequencial com GET + POST controlado nos fluxos críticos.

Script executado:
- `powershell -ExecutionPolicy Bypass -File scripts/smoke_etapa2_baseline.ps1`

Resultado por etapa:
1. `manage.py check` -> OK
2. Regressão dirigida -> `100 passed`
3. Smoke HTTP local:
   - `SMOKE_CONEXOES:/conexoes/perfil/sections/conexoes/|200`
   - `SMOKE_PIX_GET:/pagamentos/checkout/pix/|200`
   - `SMOKE_FATURAMENTO_GET:/pagamentos/checkout/faturamento/|200`
   - `SMOKE_MEMBROS_POST_INVALID:/membros/3/promover/form/|400`
   - `SMOKE_PIX_POST:/pagamentos/checkout/pix/|302`
   - `SMOKE_FAT_POST:/pagamentos/checkout/faturamento/|302`

Observação:
- O `400` de membros é comportamento esperado para cenário inválido controlado (coordenação sem papel).

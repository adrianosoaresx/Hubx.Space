# Smoke Etapa 2 - Script Rapido

Data: 2026-03-10 18:07:58
Escopo: validar execução do smoke rápido diário (sem pytest), focado em endpoints e POSTs controlados.

Script executado:
- `powershell -ExecutionPolicy Bypass -File scripts/smoke_etapa2_rapido.ps1`

Resultado:
- `SMOKE_CONEXOES:/conexoes/perfil/sections/conexoes/|200`
- `SMOKE_PIX_GET:/pagamentos/checkout/pix/|200`
- `SMOKE_FATURAMENTO_GET:/pagamentos/checkout/faturamento/|200`
- `SMOKE_MEMBROS_POST_INVALID:/membros/3/promover/form/|400` (esperado)
- `SMOKE_PIX_POST:/pagamentos/checkout/pix/|302`
- `SMOKE_FAT_POST:/pagamentos/checkout/faturamento/|302`

Histórico automático:
- `docs/etapas/smoke_etapa2_rapido_history.md` atualizado com status `SUCCESS`.

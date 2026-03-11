# Smoke Scripts - Operação Local

Este guia define qual script usar no dia a dia da Etapa 2 e como interpretar o resultado.

## 1) Qual script usar

- `scripts/smoke_etapa2_rapido.ps1`
  - quando usar:
    - validação rápida entre alterações
    - checagem funcional diária
  - executa:
    - smoke HTTP local com GET + POST controlado
  - não executa:
    - suíte pytest

- `scripts/smoke_etapa2_baseline.ps1`
  - quando usar:
    - fechamento de fatia/iteração
    - preparação de handoff
    - validação antes de mudanças estruturais maiores
  - executa:
    - `manage.py check`
    - regressão dirigida (`pytest` dos módulos críticos)
    - smoke HTTP local com GET + POST controlado

## 2) Comandos prontos

- Smoke rápido:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/smoke_etapa2_rapido.ps1
```

- Baseline completo:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/smoke_etapa2_baseline.ps1
```

## 3) Critério de sucesso

- execução termina com mensagem:
  - `Smoke rapido da Etapa 2 concluido com sucesso.`
  - ou `Smoke baseline da Etapa 2 concluido com sucesso.`
- códigos esperados nos POSTs controlados:
  - `membros` inválido: `400` (esperado)
  - `pagamentos` pix: `302`
  - `pagamentos` faturamento: `302`

## 4) Histórico automático

- baseline:
  - `docs/etapas/smoke_etapa2_baseline_history.md`
- rápido:
  - `docs/etapas/smoke_etapa2_rapido_history.md`

Cada execução registra:
- timestamp
- status (`SUCCESS`/`FAIL`)
- status por etapa

## 5) Falha - ação imediata

1. Reexecutar o mesmo script para confirmar reprodutibilidade.
2. Se persistir:
   - rodar baseline completo (`smoke_etapa2_baseline.ps1`).
3. Registrar evidência em `docs/etapas/` com timestamp e erro observado.

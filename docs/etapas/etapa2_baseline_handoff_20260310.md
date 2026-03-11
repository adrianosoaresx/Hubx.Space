# Etapa 2 - Baseline Final e Handoff Local

Data: 2026-03-10
Status: pronto para transição de onda

## 1) Baseline operacional

Script único de execução sequencial:
- `scripts/smoke_etapa2_baseline.ps1`
- histórico automático por execução:
  - `docs/etapas/smoke_etapa2_baseline_history.md`

Script rápido diário (sem pytest):
- `scripts/smoke_etapa2_rapido.ps1`
- histórico automático por execução:
  - `docs/etapas/smoke_etapa2_rapido_history.md`

Comando padrão:
- `powershell -ExecutionPolicy Bypass -File scripts/smoke_etapa2_baseline.ps1`

Última execução validada:
- `docs/etapas/smoke_etapa2_baseline_script_post_controlado_20260310_180149.md`
- entrada mais recente no histórico:
  - `2026-03-10 18:04:20` (`status: SUCCESS`)
- validação do script rápido:
  - `docs/etapas/smoke_etapa2_rapido_script_20260310_180758.md`

## 2) Matriz de cobertura por fluxo crítico

| Módulo | Fluxo crítico | Cobertura de aplicação | Smoke funcional | Status |
|---|---|---|---|---|
| membros | promoção completa (seleção, conflitos, persistência, estado, contexto) | `tests/membros/test_application_promotion_*` | `smoke_onda3_membros_promotion_workflow_20260310_170417.md` | OK |
| pagamentos | checkout pix unificado | `tests/pagamentos/test_application_pix_checkout_use_case.py` | `smoke_onda3_pagamentos_pix_checkout_use_case_20260310_172420.md` | OK |
| pagamentos | checkout faturamento unificado | `tests/pagamentos/test_application_faturamento_checkout_use_case.py` | `smoke_onda3_pagamentos_faturamento_use_case_20260310_172815.md` | OK |
| pagamentos | fachada de casos de uso | `tests/pagamentos/test_application_use_cases_facade.py` | `smoke_onda3_pagamentos_use_case_facade_20260310_173157.md` | OK |
| webhooks | assinatura + known transaction | `tests/webhooks/*` e `tests/pagamentos/test_webhook_views_known_transaction.py` | `smoke_onda3_webhooks_signature_flow_20260310_153932.md` | OK |
| notificacoes | dropdown/lista de entrega | `tests/notificacoes/*` | `smoke_onda3_notificacoes_dropdown_lista_20260310_155204.md` | OK |
| audit | normalização payload/severidade | `tests/audit/*` | `smoke_onda3_audit_middleware_operacoes_reais_20260310_161724.md` | OK |
| conexoes/feed | normalização e interação | `tests/conexoes/*` + `tests/feed/*` | `smoke_onda3_conexoes_feed_interaction_20260310_162312.md` | OK |

## 3) Estado técnico de risco

- Regressão dirigida atual: `100 passed`
- Warnings de depreciação relevantes (Django 6.0): tratados nesta rodada (baseline sem warnings no pacote dirigido).
- Warning de paginação não ordenada em `conexoes`: mitigado com ordenação explícita antes do `Paginator`.

## 4) Padrões consolidados

- Use-cases de `application` como orquestradores de fluxo.
- Views como adapters HTTP/HTMX.
- Contratos internos com DTOs nos fluxos críticos já extraídos.
- Fachada de casos de uso em `apps/backend/app/modules/pagamentos/application/use_cases.py`.

## 5) Checklist de prontidão para próxima onda

1. Script baseline único executando em ambiente local: `OK`
2. Regressão crítica verde: `OK`
3. Smokes de negócio por domínio crítico registrados: `OK`
4. Smoke baseline com POST controlado (`membros` inválido esperado + `pagamentos` Pix/Faturamento): `OK`
5. Documentação de iterações e rollback local por fatia: `OK`
6. Dependência de integração externa isolada em smoke via stub local quando necessário: `OK`

## 6) Rollback local da baseline (sem Git)

1. Reverter arquivos alterados da onda alvo (manter referência nos docs `onda*_iteracao_*.md`).
2. Executar `powershell -ExecutionPolicy Bypass -File scripts/smoke_etapa2_baseline.ps1`.
3. Confirmar retorno ao estado esperado (`manage.py check` + regressão crítica verde).

## 7) Próximas ações recomendadas (24-48h)

1. Automatizar publicação do resultado do baseline script em arquivo de evidência com timestamp (append log local).
2. Iniciar a próxima onda de refatoração com base na matriz de cobertura acima, preservando o padrão DTO/use-case/fachada.
3. Priorizar estabilização de cenários de escrita de maior risco (webhooks/status) no mesmo padrão de smoke controlado.

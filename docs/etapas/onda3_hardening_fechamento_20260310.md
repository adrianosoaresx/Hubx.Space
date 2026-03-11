# Onda 3.4 - Hardening Fechamento

Data: 2026-03-10
Status: concluido

## Objetivo
Fechar hardening da Onda 3 com foco em estabilidade operacional, contratos de aplicação e redução de risco de regressão.

## Entregas tecnicas
- Estabilização de paginação em `conexoes`:
  - `conexoes/views.py`
  - ajuste aplicado: ordenação explícita (`order_by("id")`) quando queryset não ordenado antes de paginar.
  - efeito: remoção de `UnorderedObjectListWarning` nos testes de regressão.
- Consolidação de contratos em `pagamentos`:
  - fachada única de casos de uso já aplicada em `apps/backend/app/modules/pagamentos/application/use_cases.py`.
  - views consumindo ponto único de entrada da camada `application`.

## Checklist de contratos (status)

| Módulo | Fluxo crítico | Contrato de aplicação | Status |
|---|---|---|---|
| membros | promoção (parse + validação + persistência + sync + contexto) | DTO/use-case + serviços de aplicação | OK |
| pagamentos | checkout pix | use-case unificado + fachada `use_cases` | OK |
| pagamentos | checkout faturamento | use-case unificado + fachada `use_cases` | OK |
| webhooks | confirmação known transaction + assinatura | fluxo de aplicação extraído | OK |
| notificacoes | dropdown/lista entrega | fluxo de aplicação extraído | OK |
| audit | normalização payload/severidade | serviço de aplicação extraído | OK |
| conexoes/feed | normalização de evento/interaction | serviço de aplicação extraído | OK |

## Cobertura de regressão executada
- `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q`
- Resultado: `100 passed, 4 warnings`.

## Warnings residuais (não bloqueantes)
1. `RemovedInDjango60Warning` em `CheckConstraint.check` (migrations/modelos legados).
2. `RemovedInDjango60Warning` em `forms.URLField.assume_scheme` (comportamento futuro de URLField).

Observação:
- O warning de paginação não ordenada em `conexoes` foi removido neste hardening.

## Evidências
- Smoke hardening conexoes:
  - `docs/etapas/smoke_onda3_hardening_conexoes_paginacao_20260310_173619.md`
- Regressão completa com warning reduzido:
  - execução registrada na sessão desta etapa.

## Rollback local (sem Git)
1. Reverter ajuste em `conexoes/views.py` removendo ordenação condicional antes do `Paginator`.
2. Reexecutar regressão:
   - `./.venv/Scripts/python.exe -m pytest tests/conexoes tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/feed -q`
3. Confirmar retorno do warning de paginação para validar reversão.

## Próximo passo recomendado (Onda 4)
1. Tratar warnings de depreciação Django 6.0 (constraints + URLField).
2. Formalizar matriz de contratos OpenAPI REST para fluxos expostos.
3. Definir baseline de smoke automatizado por módulo crítico (script local sem dependência externa).

# Onda 4 - Iteracao Deprecations Cleanup

Data: 2026-03-10
Status: concluido

## Objetivo
Eliminar warnings de depreciação remanescentes do Django 6.0 para reduzir risco técnico de atualização.

## Entregas tecnicas
- `CheckConstraint.check` -> `CheckConstraint.condition`:
  - `nucleos/models.py`
  - `eventos/migrations/0004_inscricao_avaliacao_constraint.py`
- URLField com esquema HTTPS sem setting transitório:
  - remoção de `FORMS_URLFIELD_ASSUME_HTTPS` em `Hubx/settings.py`
  - adoção de `core.fields.URLField` (com `assume_scheme="https"`) em:
    - `eventos/models.py` (`qrcode_url`)
    - `organizacoes/models.py` (`site`, `feed_noticias`, `link`)
    - `tokens/models.py` (`TokenWebhookEvent.url`)
    - `webhooks/models.py` (`WebhookSubscription.url`)

## Validação técnica
- `./.venv/Scripts/python.exe manage.py check` -> OK
- `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q` -> `100 passed`
- Resultado de warnings na regressão: `0` warnings.

## Evidências
- Smoke de estabilidade pós-limpeza:
  - `docs/etapas/smoke_onda4_deprecations_cleanup_20260310_174820.md`

## Trade-offs
- Alteração em migration histórica (`eventos/0004`) é aceitável neste contexto local desvinculado, mas deve ser documentada para reprodutibilidade.
- Uso de `core.fields.URLField` padroniza comportamento de formulário e reduz divergência entre módulos.

## Rollback local (sem Git)
1. Reverter `condition` para `check` nos dois pontos de constraint.
2. Restaurar `models.URLField` nos modelos alterados.
3. Reintroduzir setting transitório `FORMS_URLFIELD_ASSUME_HTTPS` caso necessário.
4. Reexecutar regressão para validar retorno do baseline anterior.

## Próximo passo recomendado
Formalizar baseline final da Etapa 2 com:
1. matriz de cobertura por fluxo crítico
2. script único de smoke local sequencial
3. pacote de documentação de handoff para início da próxima onda.

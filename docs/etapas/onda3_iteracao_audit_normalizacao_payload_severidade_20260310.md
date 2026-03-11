# Onda 3.1 - Iteracao Audit Normalizacao de Payload e Severidade

Data: 2026-03-10
Status: concluido

## Objetivo
Padronizar normalizacao de status, severidade e sanitizacao de payload de auditoria na camada `application`, reduzindo regras espalhadas em middleware/service.

## Entregas
- Novo modulo application:
  - `apps/backend/app/modules/audit/application/log_normalization.py`
    - `normalize_audit_status`
    - `status_from_http_code`
    - `severity_from_status`
    - `build_audit_action`
    - `sanitize_metadata` (recursivo)
    - `enrich_metadata`
- Refactor em `audit/services.py`:
  - status normalizado antes de persistir (`SUCCESS`/`FAILURE`)
  - metadata enriquecido com severidade e sanitizacao centralizada
- Refactor em `audit/middleware.py`:
  - uso de `status_from_http_code` e `build_audit_action` para padrao unico

## Testes adicionados
- `tests/audit/test_application_log_normalization.py`
- `tests/audit/test_services_log_audit.py`
- `tests/audit/test_middleware_audit.py`

## Validacao tecnica
- `./.venv/Scripts/python.exe manage.py check` -> OK
- `./.venv/Scripts/python.exe -m pytest tests/audit -q` -> 8 passed
- Regressao dirigida plataforma:
  - `./.venv/Scripts/python.exe -m pytest tests/audit tests/notificacoes tests/pagamentos tests/webhooks -q` -> 46 passed
- Smoke funcional registrado em:
  - `docs/etapas/smoke_onda3_audit_middleware_operacoes_reais_20260310_161724.md`

## Riscos e trade-offs
- Trade-off: severidade foi persistida dentro de `metadata` para evitar migracao de schema neste slice.
- Risco residual: atualmente apenas prefixo `/membros/` e auditado por middleware; ampliacao de cobertura por dominio deve ser feita por ondas para evitar volume excessivo de logs.

## Rollback local (sem Git)
1. Remover arquivo `apps/backend/app/modules/audit/application/log_normalization.py`.
2. Reverter `audit/services.py` e `audit/middleware.py` para logica inline anterior.
3. Remover testes novos em `tests/audit/`.
4. Reexecutar:
   - `./.venv/Scripts/python.exe manage.py check`
   - `./.venv/Scripts/python.exe -m pytest tests/audit tests/notificacoes tests/pagamentos tests/webhooks -q`

## Proximo passo recomendado
Seguir na Onda 3.1 com hardening de `conexoes/feed` (eventos de interacao e notificacao cruzada) mantendo extracao incremental por slice + smoke controlado com usuario de negocio.

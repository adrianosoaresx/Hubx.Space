# Onda 3.2 - Iteracao Membros Membership Policies

Data: 2026-03-10
Status: concluido

## Objetivo
Extrair regras de autorizacao e decisao de status/tipo de membro para camada `application`, reduzindo acoplamento em `membros/views.py` e preparando evolucao incremental de promocao/admissao.

## Entregas
- Novo modulo application:
  - `apps/backend/app/modules/membros/application/membership_policies.py`
    - `resolve_allowed_user_types_for_creator`
    - `can_access_promocao`
    - `parse_promote_associado_flag`
    - `resolve_membership_target_user_type`
    - `should_clear_primary_nucleo`
- Refactor em `membros/views.py`:
  - `MembrosPromocaoPermissionMixin` agora usa `can_access_promocao`.
  - `OrganizacaoUserCreateView.get_allowed_user_types` delega para policy.
  - parsing de `promover_associado` delegado para policy.
  - decisao de limpar `nucleo` principal e recalcular `user_type` delegadas para policy.

## Testes adicionados
- `tests/membros/test_application_membership_policies.py`
  - cobertura de politicas de acesso, parse de flag e resolucao de tipo alvo.

## Validacao tecnica
- `./.venv/Scripts/python.exe manage.py check` -> OK
- `./.venv/Scripts/python.exe -m pytest tests/membros -q` -> 12 passed
- Regressao dirigida plataforma:
  - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q` -> 69 passed
- Smoke funcional registrado em:
  - `docs/etapas/smoke_onda3_membros_promocao_admissao_acesso_20260310_162726.md`

## Riscos e trade-offs
- Trade-off: neste slice, foco em regras de politica e acesso; nao houve extracao da transacao completa de promocao (bloco de mutacao extensa) para evitar regressao funcional.
- Risco residual: `MembroPromoverFormView.post` permanece extenso e merece fatiamento adicional por etapas (validacao, conflito de papeis, persistencia) na proxima iteracao.

## Rollback local (sem Git)
1. Remover `apps/backend/app/modules/membros/application/membership_policies.py`.
2. Reverter chamadas em `membros/views.py` para logica inline anterior.
3. Remover `tests/membros/test_application_membership_policies.py`.
4. Reexecutar:
   - `./.venv/Scripts/python.exe manage.py check`
   - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q`

## Proximo passo recomendado
Continuar Onda 3.2 em `membros` com slice focado no `MembroPromoverFormView.post`: extrair validacoes de conflito (papel/consultoria/remocao) para `application` e preservar persistencia transacional na view.

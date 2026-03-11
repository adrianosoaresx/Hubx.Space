# Onda 2 - Kickoff tecnico (accounts e tokens)

Data: 10/03/2026

## Objetivo desta entrega

Iniciar migracao incremental da Onda 2 sem quebrar rotas existentes, movendo
regras de negocio pontuais para a camada `application`.

## Mudancas aplicadas

1. Criacao de caso de uso em `accounts`:
   - `apps/backend/app/modules/accounts/application/profile_permissions.py`
   - funcoes extraidas:
     - `can_manage_profile`
     - `can_promote_profile`

2. Criacao de caso de uso em `tokens`:
   - `apps/backend/app/modules/tokens/application/invite_flow.py`
   - funcoes extraidas:
     - `redirect_root_from_tokens`
     - `get_query_param`
     - `build_invite_totals`

3. Delegacao nas views atuais (sem alterar contratos HTTP):
   - `accounts/views.py` passa a chamar os casos de uso de permissao de perfil.
   - `tokens/views.py` passa a chamar os casos de uso do fluxo de convite.

4. Pacotes Python habilitados para import no monorepo:
   - `apps/__init__.py`
   - `apps/backend/__init__.py`
   - `apps/backend/app/__init__.py`
   - `apps/backend/app/modules/__init__.py`
   - `apps/backend/app/modules/accounts/__init__.py`
   - `apps/backend/app/modules/tokens/__init__.py`

## Resultado esperado

- Nenhuma mudanca de URL, payload ou template.
- Regras selecionadas agora estao desacopladas de controller.
- Padrao replicavel para proximos modulos da Onda 2.

## Proxima iteracao sugerida

1. Extrair casos de uso de autenticacao em `accounts` (login/MFA).
2. Extrair fluxo de emissao/validacao de token em `tokens`.
3. Adicionar testes focados em casos de uso (unitarios) antes de ampliar a migracao.


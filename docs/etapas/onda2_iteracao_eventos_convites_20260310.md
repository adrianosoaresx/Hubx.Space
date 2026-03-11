# Onda 2 - Iteracao Eventos Convites Publicos

Data: 2026-03-10 14:15:08

## Escopo executado
- Extracao de fluxo de convites publicos para camada `application`:
  - `apps/backend/app/modules/eventos/application/public_invites.py`
    - `get_public_invite_token_generator`
    - `is_public_invite_token_reusable`
    - `create_public_invite_token`
- Delegacao aplicada em `eventos/views.py`:
  - `_criar_token_convite_publico` agora usa `create_public_invite_token`
- Correcao de bug de template descoberto no smoke:
  - `eventos/templates/eventos/convites/public.html` adicionando `{% load static %}`

## Testes adicionados
- `tests/eventos/test_eventos_application_public_invites.py`

## Validacao
- `python manage.py check` OK
- Suite direcionada Onda 2: 53 passed, 4 warnings
- Smoke funcional com usuario de negocio e convite publico: 
  - `docs/etapas/smoke_onda2_eventos_convites_20260310_141455.md`

## Risco tratado
- Regressao em convite publico reduzida com testes do fluxo de reutilizacao/criacao de token.
- Erro de renderizacao de template corrigido e validado em smoke.

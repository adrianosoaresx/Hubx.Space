# Onda 2 - Iteracao Eventos Convites Public Flow

Data: 2026-03-10 15:16:16

## Escopo executado
- Extracao de regras do fluxo publico de convite para camada `application`:
  - `apps/backend/app/modules/eventos/application/public_invite_flow.py`
    - `build_login_redirect_url`
    - `build_register_url`
    - `build_public_invite_email_context`
    - `build_public_invite_email_subject`
    - `build_public_invite_info_context`
    - `build_public_invite_page_context`
- Delegacao aplicada em `eventos/views.py`:
  - `convite_public_view` (montagem de URLs, assunto/contexto de e-mail e contextos de resposta)

## Testes adicionados
- `tests/eventos/test_eventos_application_public_invite_flow.py`

## Validacao
- `.\.venv\Scripts\python.exe manage.py check` OK
- Suite direcionada Onda 2: 116 passed, 4 warnings
- Smoke funcional com usuario de negocio com organizacao/permissoes validas:
  - `docs/etapas/smoke_onda2_eventos_convites_public_flow_20260310_151616.md`

## Observacao
- O comportamento de redirecionamento para login com `next` foi preservado para e-mail ja cadastrado no fluxo publico de convite.

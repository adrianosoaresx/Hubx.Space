# Onda 2 - Iteracao Eventos Convites Create

Data: 2026-03-10 15:11:58

## Escopo executado
- Extracao de regras do fluxo de criacao de convite para camada `application`:
  - `apps/backend/app/modules/eventos/application/invite_management.py`
    - `can_user_manage_convites`
    - `build_convite_create_context`
- Delegacao aplicada em `eventos/views.py`:
  - `convite_create` (autorizacao por perfil e montagem de contexto)

## Testes adicionados
- `tests/eventos/test_eventos_application_invite_management.py`

## Correcao adicional identificada no smoke
- Ajuste de template com tag `static` sem carregamento da biblioteca:
  - `eventos/templates/eventos/convites/form.html`

## Validacao
- `.\.venv\Scripts\python.exe manage.py check` OK
- Suite direcionada Onda 2: 110 passed, 4 warnings
- Smoke funcional com usuario de negocio com organizacao/permissoes validas:
  - `docs/etapas/smoke_onda2_eventos_convites_create_20260310_151158.md`

## Observacao
- O fluxo publico de convite foi validado com e-mail ja existente, preservando o comportamento de redirecionar para login com parametro `next` para o overview de inscricao do evento.

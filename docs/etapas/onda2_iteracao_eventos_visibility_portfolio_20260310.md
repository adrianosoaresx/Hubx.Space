# Onda 2 - Iteracao Eventos Visibility Portfolio

Data: 2026-03-10 14:56:26

## Escopo executado
- Expansao do modulo `application` de visibilidade:
  - `apps/backend/app/modules/eventos/application/visibility.py`
    - `is_user_event_coordinator`
    - `has_restricted_event_access`
    - `can_manage_event_portfolio`
    - `can_view_event_subscribers`
- Delegacao aplicada em `eventos/views.py`:
  - `_usuario_eh_coordenador_do_evento`
  - `_usuario_tem_acesso_restrito_evento`
  - `_usuario_pode_gerenciar_portfolio`
  - `_usuario_pode_ver_inscritos`

## Testes atualizados
- `tests/eventos/test_eventos_application_visibility.py`
  - novos casos para coordenacao de evento, acesso restrito, permissao de portfolio e visualizacao de inscritos

## Correcao adicional identificada no smoke
- Ajuste de fallback de navegacao nos templates de portfolio, removendo dependencia direta de `request.META.HTTP_REFERER`:
  - `eventos/templates/eventos/portfolio/form.html`
  - `eventos/templates/eventos/portfolio/confirm_delete.html`

## Validacao
- `.\.venv\Scripts\python.exe manage.py check` OK
- Suite direcionada Onda 2: 102 passed, 4 warnings
- Smoke funcional com usuario de negocio com organizacao/permissoes validas:
  - `docs/etapas/smoke_onda2_eventos_visibility_portfolio_20260310_145626.md`

## Observacao
- Com a extracao, as regras de acesso restrito/coordenacao/portfolio ficaram centralizadas em `application`, reduzindo duplicacao e facilitando evolucoes futuras de autorizacao por perfil.

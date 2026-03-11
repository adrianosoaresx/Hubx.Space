# Onda 3.2 - Iteracao Membros Promotion Form Context Extraction

Data: 2026-03-10
Status: concluido

## Objetivo
Extrair a montagem de contexto da tela de promoção (`_build_form_context`) para a camada `application`, reduzindo acoplamento de consulta/renderização na view.

## Entregas
- Novo query service:
  - `apps/backend/app/modules/membros/application/promotion_form_context.py`
    - `build_promocao_form_context`
    - responsabilidades:
      - carregar núcleos da organização com coordenações ativas
      - compor flags de vínculo atual do membro (participação, consultoria, coordenação)
      - construir mensagens de papéis indisponíveis
      - normalizar estado selecionado da UI e mapa de papéis
- Refactor em `membros/views.py`:
  - `_build_form_context` passou a delegar integralmente para `build_promocao_form_context`
  - remoção de imports agora internos ao serviço (`json`, `defaultdict`, `Prefetch`)

## Testes adicionados
- `tests/membros/test_application_promotion_form_context.py`
  - valida flags e mensagens de indisponibilidade
  - valida mapa de papéis atuais do usuário no contexto (`user_role_map_json`)

## Validação técnica
- `./.venv/Scripts/python.exe manage.py check` -> OK
- `./.venv/Scripts/python.exe -m pytest tests/membros/test_application_promotion_form_context.py -q` -> 2 passed
- `./.venv/Scripts/python.exe -m pytest tests/membros -q` -> 27 passed
- Regressão dirigida plataforma:
  - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q` -> 84 passed
- Smoke funcional registrado em:
  - `docs/etapas/smoke_onda3_membros_promotion_form_context_20260310_165845.md`

## Riscos e trade-offs
- Trade-off: serviço ainda retorna dicionário pronto para template (orientado a view), priorizando estabilidade de integração HTMX.
- Risco residual: regras de apresentação e formatação ainda estão juntas no mesmo serviço; futura divisão possível entre query + presenter.

## Rollback local (sem Git)
1. Remover `apps/backend/app/modules/membros/application/promotion_form_context.py`.
2. Restaurar implementação inline de `_build_form_context` em `membros/views.py`.
3. Remover `tests/membros/test_application_promotion_form_context.py`.
4. Reexecutar:
   - `./.venv/Scripts/python.exe manage.py check`
   - `./.venv/Scripts/python.exe -m pytest tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q`

## Próximo passo recomendado
Extrair o comando completo de promoção (validação + persistência + sincronização de estado) para um `application use-case`, deixando a view apenas como adapter HTTP/HTMX.

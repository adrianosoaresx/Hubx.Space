# Onda 3.1 - Iteracao Conexoes e Feed Event Normalization

Data: 2026-03-10
Status: concluido

## Objetivo
Padronizar eventos de interacao/notificacao de `conexoes` e `feed` em camada `application`, reduzindo duplicacao de regras em views/tasks e mantendo execucao incremental.

## Entregas
- Novo modulo application `conexoes`:
  - `apps/backend/app/modules/conexoes/application/connection_notifications.py`
    - `resolve_connection_template`
    - `build_connection_notification_context`
- Novo modulo application `feed`:
  - `apps/backend/app/modules/feed/application/interaction_notifications.py`
    - `resolve_interaction_template`
    - `build_interaction_notification_context`
- Refactor em `conexoes/views.py`:
  - `_dispatch_connection_notification` agora resolve template/contexto padronizados.
  - fluxos `solicitar`, `aceitar` e `recusar` usam o mesmo dispatcher.
  - elimina dependência implícita de envio síncrono direto e centraliza agendamento.
- Refactor em `feed/tasks.py`:
  - `notificar_autor_sobre_interacao` usa resolver de template/contexto padronizado.

## Testes adicionados
- `tests/conexoes/test_application_connection_notifications.py`
- `tests/conexoes/test_views_connection_notifications.py`
- `tests/feed/test_application_interaction_notifications.py`
- `tests/feed/test_tasks_interaction_notifications.py`

## Validacao tecnica
- `./.venv/Scripts/python.exe manage.py check` -> OK
- `./.venv/Scripts/python.exe -m pytest tests/conexoes tests/feed -q` -> 11 passed
- Regressao dirigida plataforma:
  - `./.venv/Scripts/python.exe -m pytest tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed -q` -> 57 passed
- Smoke funcional registrado em:
  - `docs/etapas/smoke_onda3_conexoes_feed_interaction_20260310_162312.md`

## Riscos e trade-offs
- Trade-off: notificação de conexão permanece com envio assíncrono via Celery task; no smoke, validamos agendamento e notificacao de feed com execução direta da task para garantir determinismo local.
- Risco residual: warning de paginação em conexoes (`UnorderedObjectListWarning`) indica oportunidade de ordenar queryset antes do paginator.

## Rollback local (sem Git)
1. Remover arquivos:
   - `apps/backend/app/modules/conexoes/application/connection_notifications.py`
   - `apps/backend/app/modules/feed/application/interaction_notifications.py`
2. Reverter `conexoes/views.py` e `feed/tasks.py` para lógica inline anterior.
3. Remover testes novos em `tests/conexoes/` e `tests/feed/`.
4. Reexecutar:
   - `./.venv/Scripts/python.exe manage.py check`
   - `./.venv/Scripts/python.exe -m pytest tests/conexoes tests/feed tests/notificacoes tests/pagamentos tests/webhooks tests/audit -q`

## Proximo passo recomendado
Entrar na Onda 3.2 com `membros`: extrair políticas de vínculo/status/autorização em `application` e rodar smoke de promoção/admissão com usuário de negócio e organização válida.

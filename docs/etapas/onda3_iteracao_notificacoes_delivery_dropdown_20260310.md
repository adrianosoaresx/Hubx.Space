# Onda 3.1 - Iteracao Notificacoes Delivery e Dropdown

Data: 2026-03-10
Status: concluido

## Objetivo
Extrair regras de montagem de conteudo/canais de entrega e resolucao de destino do dropdown para camada `application`, mantendo comportamento atual da interface web e do envio assíncrono.

## Entregas
- Novo modulo application (delivery):
  - `apps/backend/app/modules/notificacoes/application/delivery_planning.py`
    - `render_notification_content`
    - `mask_email`
    - `resolve_channels_for_delivery`
    - `resolve_destinatario`
- Novo modulo application (dropdown):
  - `apps/backend/app/modules/notificacoes/application/dropdown_targets.py`
    - `resolve_dropdown_target_url`
- Refactor em:
  - `notificacoes/services/notificacoes.py`
    - delegacao de renderizacao, escolha de canais e destinatario.
  - `notificacoes/views.py`
    - delegacao de target URL do dropdown.
- Correcao oportunistica de template:
  - `notificacoes/templates/notificacoes/notificacoes_list.html`
    - adicionado `{% load static %}` para eliminar erro em runtime.

## Testes adicionados
- `tests/notificacoes/test_application_delivery_planning.py`
- `tests/notificacoes/test_application_dropdown_targets.py`
- `tests/notificacoes/test_views_dropdown.py`

## Validacao tecnica
- `./.venv/Scripts/python.exe manage.py check` -> OK
- `./.venv/Scripts/python.exe -m pytest tests/notificacoes -q` -> 10 passed
- Regressao dirigida:
  - `./.venv/Scripts/python.exe -m pytest tests/notificacoes tests/pagamentos tests/webhooks -q` -> 38 passed
- Smoke funcional registrado em:
  - `docs/etapas/smoke_onda3_notificacoes_dropdown_lista_20260310_155204.md`

## Riscos e trade-offs
- Trade-off: foco em regras de montagem e roteamento de UI, sem alterar orquestracao de task assíncrona (`enviar_notificacao_async`).
- Risco residual: ainda existe acoplamento parcial de persistencia/log dentro do service legado; proxima fatia pode separar factories de log (falha/sucesso) para `application`.

## Rollback local (sem Git)
1. Remover arquivos:
   - `apps/backend/app/modules/notificacoes/application/delivery_planning.py`
   - `apps/backend/app/modules/notificacoes/application/dropdown_targets.py`
2. Reverter delegacoes em:
   - `notificacoes/services/notificacoes.py`
   - `notificacoes/views.py`
3. Se necessario, remover testes novos em `tests/notificacoes/`.
4. Reexecutar:
   - `./.venv/Scripts/python.exe manage.py check`
   - `./.venv/Scripts/python.exe -m pytest tests/notificacoes tests/pagamentos tests/webhooks -q`

## Proximo passo recomendado
Avancar para `audit` na Onda 3.1: padronizar evento de auditoria em `application` (normalizacao de payload e severidade) e smoke com operacoes de negocio reais.

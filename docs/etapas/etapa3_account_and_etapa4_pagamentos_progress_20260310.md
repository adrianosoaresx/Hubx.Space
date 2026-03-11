# Etapa 3 (Account) + Início Etapa 4 (Pagamentos) - Progresso

Data: 2026-03-10

## Status geral

- Etapa 3 (`account`) avançou para um piloto funcional extenso com migração incremental:
  - gestão de status de usuário (ativar/desativar)
  - perfil/info (render + edição)
  - recuperação de conta (confirm-email, resend-confirmation, request/reset password)
  - autenticação com 2FA (helpers de sessão/redirect e regras MFA extraídas)
- Início da Etapa 4 (`pagamentos`) executado no slice de retorno de checkout Mercado Pago:
  - validação de status de retorno
  - resolução de mensagem de retorno
  - lookup de transação por token/id

## Arquitetura aplicada

### Account

- `apps/backend/app/modules/accounts/domain/`
  - `exceptions.py`
  - `profile_management.py`
  - `account_recovery.py`
- `apps/backend/app/modules/accounts/application/`
  - `profile_management.py`
  - `profile_info.py`
  - `authentication_flow.py`
  - `mfa_login_flow.py`
  - `account_recovery.py`
- `apps/backend/app/modules/accounts/infrastructure/`
  - `profile_management.py`
  - `profile_info.py`
  - `authentication_flow.py`
  - `account_recovery.py`
- `apps/backend/app/modules/accounts/interfaces/`
  - `profile_management.py`
  - `account_recovery.py`

### Pagamentos (kickoff Etapa 4)

- `apps/backend/app/modules/pagamentos/domain/`
  - `payment_return.py`
- `apps/backend/app/modules/pagamentos/application/`
  - `payment_return_flow.py`
- `apps/backend/app/modules/pagamentos/infrastructure/`
  - `payment_return_lookup.py`
  - `transacao_status_lookup.py`
  - `payment_webhook_orchestration.py` (via application orchestration + adapters em view)

## Integração no legado

- `accounts/views.py` e `accounts/api.py` delegando para casos de uso do módulo.
- `pagamentos/views.py` (MercadoPagoRetornoView) delegando para use case + repository do módulo.
- `packages/contracts/openapi.yaml` atualizado para endpoints REST de recuperação/gestão de conta e endpoints REST/HTTP operacionais de pagamentos.

## Evidências de teste

- `pytest tests/accounts -q` -> passou
- `pytest tests/pagamentos tests/accounts -q` -> passou
- `manage.py check` -> sem issues
- suíte ampliada (`tests/membros tests/audit tests/notificacoes tests/pagamentos tests/webhooks tests/conexoes tests/feed tests/accounts`) -> passou
- smoke pós-OpenAPI pagamentos:
  - `pytest tests/pagamentos/test_webhook_views_signature_and_unknown.py tests/pagamentos/test_views_transacao_status.py tests/pagamentos/test_views_transacao_reporting.py -q` -> `6 passed`
  - `pytest tests/pagamentos/test_webhook_views_known_transaction.py tests/pagamentos/test_views_mercadopago_retorno.py -q` -> `3 passed`
- validação de contrato:
  - parse local do `packages/contracts/openapi.yaml` via `yaml.safe_load` -> OK

## Avanço adicional na Etapa 4 (2026-03-10)

- `TransacaoStatusView` migrado para decisão em caso de uso (`application/transacao_status_flow.py`).
- `WebhookView`/`PayPalWebhookView` passaram a delegar para orquestração de aplicação:
  - `application/payment_webhook_orchestration.py`
  - `views.py` mantém responsabilidade de interface HTTP.
- `TransacaoRevisaoView` e `TransacaoCSVExportView` migrados para regras de reporting em application:
  - `application/transacao_reporting.py`
  - `infrastructure/transacao_reporting_lookup.py`
- `PixCheckoutView` e `FaturamentoView` com redução de acoplamento via adapters:
  - `application/checkout_inscricao_flow.py` (montagem de dados iniciais de inscrição)
  - `infrastructure/checkout_inscricao_repository.py` (lookup/acesso + vínculo de transação + faturamento)
- Testes adicionados:
  - `tests/pagamentos/test_application_transacao_status_flow.py`
  - `tests/pagamentos/test_views_transacao_status.py`
  - `tests/pagamentos/test_application_payment_webhook_orchestration.py`
  - `tests/pagamentos/test_webhook_views_signature_and_unknown.py`
  - `tests/pagamentos/test_application_transacao_reporting.py`
  - `tests/pagamentos/test_views_transacao_reporting.py`
  - `tests/pagamentos/test_application_checkout_inscricao_flow.py`

## Avanço incremental em Account (login/MFA - 2026-03-10)

- Refatoração de interface em `accounts/views.py` para reduzir acoplamento direto com sessão no fluxo 2FA:
  - criação de helper `_issue_pending_login_email_challenge(...)` para unificar emissão de desafio por e-mail e feedback ao usuário;
  - remoção de acesso direto a chaves de sessão em pontos críticos de `login_view` e `login_totp`.
- Evolução de infraestrutura em `apps/backend/app/modules/accounts/infrastructure/authentication_flow.py`:
  - novos métodos no `DjangoPending2FASessionManager`:
    - `set_method(...)`
    - `get_next_url(...)`
    - `set_challenge_id(...)`
    - `get_challenge_id(...)`
    - `clear_challenge_id(...)`
- Nova cobertura de teste:
  - `tests/accounts/test_infrastructure_authentication_flow.py`
- Smokes executados:
  - `pytest tests/accounts/test_login_mfa_switch_and_resend.py tests/accounts/test_login_redirects.py tests/accounts/test_infrastructure_authentication_flow.py -q` -> `7 passed`
  - `pytest tests/accounts -q` -> `41 passed`
  - `python manage.py check` -> sem issues

## Avanço incremental em Account (exclusão de conta - 2026-03-10)

- Extração do fluxo de exclusão para camadas:
  - `apps/backend/app/modules/accounts/application/account_deletion.py`
  - `apps/backend/app/modules/accounts/infrastructure/account_deletion.py`
- `accounts/views.py` (`excluir_conta`) agora delega a operação transacional para `AccountDeletionUseCase`, mantendo a view focada em validação HTTP/HTMX, mensagens e redirecionamento.
- Paridade preservada:
  - token de cancelamento de exclusão continua sendo emitido com janela de 30 dias;
  - envio de e-mail de cancelamento continua condicionado a exclusão da própria conta (`is_self`).
- Cobertura adicionada:
  - `tests/accounts/test_application_account_deletion.py`
- Smokes executados:
  - `pytest tests/accounts/test_application_account_deletion.py tests/accounts/test_login_mfa_switch_and_resend.py tests/accounts/test_login_redirects.py -q` -> `7 passed`
  - `pytest tests/accounts -q` -> `42 passed`
  - `python manage.py check` -> sem issues

## Avanço incremental em Account (cancelamento de exclusão - 2026-03-10)

- Extração das regras de cancelamento de exclusão para camadas compartilhadas:
  - `apps/backend/app/modules/accounts/application/account_delete_cancellation.py`
  - `apps/backend/app/modules/accounts/infrastructure/account_delete_cancellation.py`
- Integração nos pontos de entrada:
  - `accounts/views.py` (`cancel_delete`) delegando para `AccountDeleteCancellationUseCase`
  - `accounts/api.py` (`me/cancel-delete`) delegando para o mesmo caso de uso
- Resultado:
  - remoção da duplicação de regra entre Web e API para validação/reativação de conta por token de cancelamento.
  - API preserva log de auditoria (`account_delete_canceled`) após sucesso.
- Cobertura adicionada:
  - `tests/accounts/test_application_account_delete_cancellation.py`
  - novos cenários em:
    - `tests/accounts/test_web_account_recovery_flows.py`
    - `tests/accounts/test_api_account_recovery_flows.py`
- Smokes executados:
  - `pytest tests/accounts/test_application_account_delete_cancellation.py tests/accounts/test_web_account_recovery_flows.py tests/accounts/test_api_account_recovery_flows.py -q` -> `14 passed`
  - `pytest tests/accounts -q` -> `49 passed`
  - `python manage.py check` -> sem issues

## Avanço incremental em Account (API delete_me unificada - 2026-03-10)

- `accounts/api.py` (`delete_me`) passou a delegar para `AccountDeletionUseCase`:
  - remove duplicação de regra de exclusão/tokennização antes implementada inline na API;
  - mantém validação existente de segurança (`password` ou `confirm == EXCLUIR`);
  - mantém envio de e-mail de cancelamento via `send_cancel_delete_email`.
- Benefício: Web (`excluir_conta`) e API (`delete_me`) agora compartilham a mesma lógica transacional de exclusão.
- Cobertura adicionada:
  - novos cenários em `tests/accounts/test_api_account_recovery_flows.py`:
    - confirmação inválida -> `400`
    - sucesso -> `204` + usuário soft-deleted/inativo + token `CANCEL_DELETE`
- Smokes executados:
  - `pytest tests/accounts/test_api_account_recovery_flows.py tests/accounts/test_application_account_deletion.py -q` -> `9 passed`
  - `pytest tests/accounts -q` -> `51 passed`
  - `python manage.py check` -> sem issues

## Avanço incremental em Account (API cancel_delete desacoplada - 2026-03-10)

- Extração do acoplamento residual de auditoria do endpoint API `me/cancel-delete`:
  - novo adapter de infraestrutura:
    - `apps/backend/app/modules/accounts/infrastructure/account_audit.py`
  - novo adapter de interface:
    - `apps/backend/app/modules/accounts/interfaces/account_delete_cancellation.py`
- `accounts/api.py` passou a:
  - delegar mapeamento de resposta HTTP para o adapter de interface;
  - delegar persistência de auditoria para `DjangoAccountAuditLogger`.
- Cobertura reforçada:
  - `tests/accounts/test_api_account_recovery_flows.py` agora valida criação do `AuditLog` (`action=account_delete_canceled`) no sucesso do cancelamento.
- Smokes executados:
  - `pytest tests/accounts/test_api_account_recovery_flows.py -q` -> `8 passed`
  - `pytest tests/accounts -q` -> `51 passed`
  - `python manage.py check` -> sem issues

## Avanço incremental em Account (API delete_me: evento de falha desacoplado - 2026-03-10)

- Extração do evento de segurança `conta_exclusao_falha` para adapters:
  - infraestrutura: `apps/backend/app/modules/accounts/infrastructure/account_security_events.py`
  - interface HTTP: `apps/backend/app/modules/accounts/interfaces/account_deletion.py`
- `accounts/api.py` (`delete_me`) agora:
  - delega registro de evento de falha para `DjangoAccountSecurityEventLogger`;
  - delega resposta HTTP de validação inválida para mapper de interface.
- Cobertura reforçada:
  - `tests/accounts/test_api_account_recovery_flows.py` valida criação de `SecurityEvent(evento=conta_exclusao_falha)` no cenário inválido.
- Smokes executados:
  - `pytest tests/accounts/test_api_account_recovery_flows.py -q` -> `8 passed`
  - `pytest tests/accounts -q` -> `51 passed`
  - `python manage.py check` -> sem issues

## Avanço incremental em Account (API 2FA desacoplada - 2026-03-10)

- `accounts/api.py` (`enable_2fa` / `disable_2fa`) passou a delegar:
  - eventos de segurança para `DjangoAccountSecurityEventLogger` (`account_security_events.py`);
  - respostas HTTP para mapper de interface `apps/backend/app/modules/accounts/interfaces/account_two_factor.py`.
- Resultado:
  - redução do acoplamento de regras de interface e side-effects de segurança dentro da viewset;
  - padronização de respostas de erro/sucesso de 2FA.
- Cobertura adicionada:
  - `tests/accounts/test_api_2fa_flows.py` cobrindo:
    - falha de senha em habilitação (evento `2fa_habilitacao_falha`)
    - habilitação em duas etapas (setup secret + confirmação com código) com evento `2fa_habilitado`
    - falha de senha em desabilitação (evento `2fa_desabilitacao_falha`)
    - desabilitação com sucesso (evento `2fa_desabilitado` + remoção de device)
- Smokes executados:
  - `pytest tests/accounts/test_api_2fa_flows.py -q` -> `4 passed`
  - `pytest tests/accounts -q` -> `55 passed`
  - `python manage.py check` -> sem issues

## Avanço incremental em Account (API rate_user desacoplada - 2026-03-10)

- Extração do bloco de agregação de avaliações do endpoint `rate_user`:
  - `apps/backend/app/modules/accounts/application/user_rating.py`
  - `apps/backend/app/modules/accounts/infrastructure/user_rating.py`
  - `apps/backend/app/modules/accounts/interfaces/user_rating.py`
- `accounts/api.py` passou a delegar:
  - cálculo de média/total/display para `UserRatingStatsUseCase`;
  - montagem de payload de resposta para adapter de interface.
- Observação:
  - validação e persistência da avaliação continuam no `UserRatingSerializer` (sem mudança funcional nesta iteração).
- Cobertura adicionada:
  - `tests/accounts/test_application_user_rating.py`
  - `tests/accounts/test_api_user_rating.py`
- Smokes executados:
  - `pytest tests/accounts/test_application_user_rating.py tests/accounts/test_api_user_rating.py -q` -> `2 passed`
  - `pytest tests/accounts -q` -> `57 passed`
  - `python manage.py check` -> sem issues

## Avanço incremental em Account (criação de rating extraída do serializer - 2026-03-10)

- Extração da criação da avaliação para camadas:
  - `apps/backend/app/modules/accounts/application/user_rating_creation.py`
  - `apps/backend/app/modules/accounts/infrastructure/user_rating_creation.py`
- `accounts/serializers.py`:
  - `UserRatingSerializer.create` passa a delegar para `UserRatingCreationUseCase`;
  - serializer permanece como adapter de entrada/validação.
- Cobertura adicionada:
  - `tests/accounts/test_application_user_rating_creation.py`
- Smokes executados:
  - `pytest tests/accounts/test_application_user_rating_creation.py tests/accounts/test_application_user_rating.py tests/accounts/test_api_user_rating.py -q` -> `3 passed`
  - `pytest tests/accounts -q` -> `58 passed`
  - `python manage.py check` -> sem issues

## Avanço incremental em Account (viewset API com adapter único de respostas - 2026-03-10)

- Consolidação de respostas recorrentes da `accounts/api.py` em adapter dedicado:
  - `apps/backend/app/modules/accounts/interfaces/account_api_responses.py`
  - cobre `201 created`, `204 no content` e payload padrão de ativação/desativação de usuário.
- `accounts/api.py`:
  - remove respostas inline repetidas em `rate_user`, `delete_me`, `activate` e `deactivate`;
  - remove imports residuais não utilizados.
- Smokes executados:
  - `pytest tests/accounts/test_profile_management_flows.py tests/accounts/test_api_account_recovery_flows.py tests/accounts/test_api_user_rating.py tests/accounts/test_api_2fa_flows.py -q` -> `16 passed`
  - `pytest tests/accounts -q` -> `58 passed`
  - `python manage.py check` -> sem issues

## Avanço incremental em Pagamentos (interfaces de resposta HTTP - 2026-03-10)

- Criação de adapter de interface para respostas HTTP recorrentes:
  - `apps/backend/app/modules/pagamentos/interfaces/http_responses.py`
- `pagamentos/views.py` passou a delegar respostas em fluxos críticos:
  - `TransacaoStatusView`: transação inválida + redirect HTMX;
  - `MercadoPagoRetornoView`: status de retorno inválido + mensagens por chave;
  - `WebhookView`: mapeamento de `missing_external_id`, `invalid_signature` e `processed`.
- Benefício:
  - padronização de resposta/erro sem alterar regra de negócio;
  - redução de lógica de interface inline em views.
- Cobertura adicionada:
  - `tests/pagamentos/test_interfaces_http_responses.py`
- Smokes executados:
  - `pytest tests/pagamentos/test_interfaces_http_responses.py tests/pagamentos/test_views_transacao_status.py tests/pagamentos/test_webhook_views_signature_and_unknown.py tests/pagamentos/test_views_mercadopago_retorno.py -q` -> `11 passed`
  - `pytest tests/pagamentos -q` -> `48 passed`
  - `python manage.py check` -> sem issues

## Avanço incremental em Pagamentos (OpenAPI com exemplos canônicos - 2026-03-10)

- `packages/contracts/openapi.yaml` enriquecido com exemplos para endpoints REST já estabilizados:
  - webhooks (`mercadopago`, `compat`, `paypal`): exemplos de payload e erro `missing id`;
  - `checkout/status/{pk}`: header `HX-Redirect` documentado em `204` e exemplo de erro `invalid transaction`;
  - `relatorios/transacoes.csv`: exemplo mínimo de CSV.
- `PaymentWebhookPayload` recebeu `example` padrão.
- Validação de contrato:
  - parse local via `yaml.safe_load` -> `openapi_ok True`, `paths 30`.

## Avanço incremental em Pagamentos (checkout/faturamento com adapter de interface - 2026-03-10)

- Criação de adapter para respostas/contexto de checkout:
  - `apps/backend/app/modules/pagamentos/interfaces/checkout_http.py`
- `pagamentos/views.py` (PixCheckoutView/FaturamentoView) passou a delegar:
  - status de erro de formulário (`400`);
  - montagem de contextos de render;
  - URL de redirect para resultado de checkout.
- Objetivo:
  - remover duplicação de respostas/contextos inline sem alterar regra de negócio.
- Cobertura adicionada:
  - `tests/pagamentos/test_interfaces_checkout_http.py`
- Smokes executados:
  - `pytest tests/pagamentos/test_interfaces_checkout_http.py tests/pagamentos/test_interfaces_http_responses.py tests/pagamentos/test_application_pix_checkout_use_case.py tests/pagamentos/test_application_faturamento_checkout_use_case.py -q` -> `14 passed`
  - `pytest tests/pagamentos -q` -> `52 passed`
  - `python manage.py check` -> sem issues

## Avanço incremental em Pagamentos (reporting com adapter de interface - 2026-03-10)

- Extração das respostas de reporting para adapter:
  - `apps/backend/app/modules/pagamentos/interfaces/reporting_http.py`
- `pagamentos/views.py` atualizado:
  - `TransacaoRevisaoView`: contexto via `build_transacao_revisao_context`;
  - `TransacaoCSVExportView`: resposta CSV via `build_transacoes_csv_response`.
- Cobertura adicionada:
  - `tests/pagamentos/test_interfaces_reporting_http.py`
- Smokes executados:
  - `pytest tests/pagamentos/test_interfaces_reporting_http.py tests/pagamentos/test_views_transacao_reporting.py -q` -> `4 passed`
  - `pytest tests/pagamentos -q` -> `54 passed`
  - `python manage.py check` -> sem issues

## Avanço incremental em Pagamentos (confirmação/sincronização extraídas para infraestrutura - 2026-03-10)

- Extração do bloco `ConfirmarPagamentoMixin` para gateway dedicado:
  - `apps/backend/app/modules/pagamentos/infrastructure/payment_confirmation_gateway.py`
- `pagamentos/views.py` passou a delegar:
  - retry de confirmação (`confirm_with_retry`);
  - sincronização de status/external_id/detalhes da transação (`sync_payment_model`).
- Resultado:
  - redução de acoplamento técnico no layer de interface;
  - preservação de comportamento em `TransacaoStatusView`, `MercadoPagoRetornoView` e `WebhookView`.
- Cobertura adicionada:
  - `tests/pagamentos/test_infrastructure_payment_confirmation_gateway.py`
- Smokes executados:
  - `pytest tests/pagamentos/test_infrastructure_payment_confirmation_gateway.py tests/pagamentos/test_views_transacao_status.py tests/pagamentos/test_webhook_views_known_transaction.py tests/pagamentos/test_webhook_views_signature_and_unknown.py tests/pagamentos/test_views_mercadopago_retorno.py -q` -> `10 passed`
  - `pytest tests/pagamentos -q` -> `57 passed`
  - `python manage.py check` -> sem issues

## Avanço incremental em Etapa 4 (integração cross-módulo eventos + pagamentos - 2026-03-10)

- Inclusão de smoke automatizado de fluxo crítico integrado:
  - inscrição em evento pago -> vínculo com transação aprovada -> polling de status de pagamento via HTMX -> redirecionamento para resultado da inscrição.
- Teste adicionado:
  - `tests/pagamentos/test_integration_eventos_pagamentos_status_result.py`
- Smokes executados:
  - `pytest tests/pagamentos/test_integration_eventos_pagamentos_status_result.py tests/pagamentos/test_views_transacao_status.py -q` -> `3 passed`
  - `pytest tests/pagamentos -q` -> `58 passed`
  - `python manage.py check` -> sem issues

## Avanço incremental em Etapa 4 (integração cross-módulo - cenário negativo - 2026-03-10)

- Inclusão de cenário negativo no fluxo `eventos + pagamentos`:
  - transação `pendente` vinculada à inscrição **não** deve disparar `HX-Redirect` para resultado.
- Teste adicionado:
  - `tests/pagamentos/test_integration_eventos_pagamentos_status_result_negative.py`
- OpenAPI ajustado:
  - `GET /pagamentos/checkout/status/{pk}` (200) com descrição explícita do cenário pendente sem redirecionamento.
- Smokes executados:
  - `pytest tests/pagamentos/test_integration_eventos_pagamentos_status_result.py tests/pagamentos/test_integration_eventos_pagamentos_status_result_negative.py tests/pagamentos/test_views_transacao_status.py -q` -> `4 passed`
  - `pytest tests/pagamentos -q` -> `59 passed`
  - parse OpenAPI (`yaml.safe_load`) -> `openapi_ok True`, `paths 30`
  - `python manage.py check` -> sem issues

## Avanço incremental em Etapa 4 (retorno sem transação vinculada + contrato REST - 2026-03-10)

- Cenário negativo explícito adicionado para retorno Mercado Pago:
  - `tests/pagamentos/test_views_mercadopago_retorno.py` agora cobre `status=sucesso` com `token` inexistente mantendo mensagem de `not_found`.
- OpenAPI atualizado para endpoint de retorno:
  - `GET /pagamentos/mp/retorno/{status}/` adicionado em `packages/contracts/openapi.yaml`
  - parâmetros de query (`token`, `payment_id`) documentados
  - exemplos canônicos para `200` (not_found) e `400` (invalid status)
- Smokes executados:
  - `pytest tests/pagamentos/test_views_mercadopago_retorno.py tests/pagamentos/test_integration_eventos_pagamentos_status_result_negative.py -q` -> `4 passed`
  - `pytest tests/pagamentos -q` -> `60 passed`
  - parse OpenAPI (`yaml.safe_load`) -> `openapi_ok True`, `paths 31`
  - `python manage.py check` -> sem issues

## Avanço incremental em Etapa 4 (cross-módulo negativo - transação falha - 2026-03-10)

- Inclusão de cenário negativo de falha no status de checkout:
  - `tests/pagamentos/test_integration_eventos_pagamentos_status_result_negative.py`
  - validação de que transação `failed`:
    - retorna `200` no endpoint de status HTMX;
    - não envia `HX-Redirect`;
    - renderiza mensagem de erro (`Pagamento falhou`).
- OpenAPI ajustado:
  - `GET /pagamentos/checkout/status/{pk}` agora explicita cenários pendente/falha sem redirect em `200`;
  - exemplo canônico `failed_no_redirect` adicionado.
- Smokes executados:
  - `pytest tests/pagamentos/test_integration_eventos_pagamentos_status_result_negative.py tests/pagamentos/test_views_transacao_status.py -q` -> `4 passed`
  - `pytest tests/pagamentos -q` -> `61 passed`
  - parse OpenAPI (`yaml.safe_load`) -> `openapi_ok True`, `paths 31`
  - `python manage.py check` -> sem issues

## Avanço incremental em Etapa 4 (matriz webhook->status + catálogo de erro OpenAPI - 2026-03-10)

- Novo cenário integrado de erro de assinatura de webhook:
  - `tests/pagamentos/test_integration_webhook_status_invalid_signature.py`
  - valida que assinatura inválida (`403`) não altera status da transação (`pending`) e não produz `HX-Redirect` indevido no status.
- OpenAPI consolidado com catálogo de erro reutilizável:
  - `components.responses` adicionados:
    - `PagamentosWebhookMissingExternalId`
    - `PagamentosWebhookInvalidSignature`
    - `PagamentosRetornoInvalidStatus`
    - `PagamentosStatusInvalidTransaction`
  - endpoints de pagamentos atualizados para referenciar respostas via `$ref`.
- Smokes executados:
  - `pytest tests/pagamentos/test_integration_webhook_status_invalid_signature.py tests/pagamentos/test_integration_eventos_pagamentos_status_result_negative.py tests/pagamentos/test_views_transacao_status.py -q` -> `5 passed`
  - `pytest tests/pagamentos -q` -> `62 passed`
  - parse OpenAPI (`yaml.safe_load`) -> `openapi_ok True`, `paths 31`, `responses 4`
  - `python manage.py check` -> sem issues

## Backlog imediato (próxima sequência)

1. Extrair remanescentes de coordenação de autenticação em `accounts/views.py` (login/MFA e registro).
2. Etapa 4 / Pagamentos: completar extrações restantes de `views.py` para adapters finos de interface.
3. OpenAPI: enriquecer exemplos de payload/erro (sem expandir escopo além de REST).

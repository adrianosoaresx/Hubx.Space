# Etapa 3 (Account) - Fechamento Formal + Backlog Etapa 4

Data: 2026-03-10  
Escopo: refatoração local em `X:\Projeto\Hubx.Space` (sem Git/PR/CI)

## 1. Decisão de fechamento

- A Etapa 3 do módulo piloto `account` está **formalmente encerrada** para o escopo definido:
  - fluxos críticos ponta a ponta ativos;
  - separação de camadas aplicada em nível suficiente para continuidade segura;
  - validação automatizada e smoke em sequência controlada.

## 2. Definition of Done (DoD) - Etapa 3 / Account

| Critério | Status | Evidência |
|---|---|---|
| Fluxos críticos ponta a ponta executam | OK | `tests/accounts` = **58 passed** |
| Separação `domain/application/infrastructure/interfaces` respeitada | OK | Estrutura em `apps/backend/app/modules/accounts/` consolidada |
| Erros e respostas mapeados em interfaces | OK | adapters em `interfaces/` para recovery, profile, 2FA, deletion, cancelation, responses |
| Regras de negócio fora de interface (incremental) | OK/PARCIAL CONTROLADO | regras críticas extraídas; `accounts/views.py` ainda contém coordenação legada de registro |
| Contrato REST coerente com fluxos já migrados | OK | endpoints account já cobertos no OpenAPI; pagamentos também atualizado no ciclo |
| Sem regressão conhecida no módulo piloto | OK | smoke dirigido + suíte completa de account |
| Pendências documentadas com prioridade | OK | seção de backlog abaixo |

## 3. Evidências objetivas (última janela)

- `pytest tests/accounts -q` -> `58 passed`
- Smokes de hardening API (`profile_management + account_recovery + user_rating + 2fa`) -> `16 passed`
- `python manage.py check` -> sem issues

## 4. Trade-offs aceitos no fechamento

1. `accounts/views.py` mantém coordenação legada de parte dos fluxos de registro para evitar big-bang.
2. Serializer de rating mantém validações de entrada; criação/agregação já extraídas para use cases.
3. Warnings de `factory_boy` permanecem não-bloqueantes nesta etapa.

## 5. Etapa 4 - Próximo módulo prioritário

Módulo prioritário: **`pagamentos`**

Racional:
- impacto direto no fluxo de receita e inscrição;
- já possui slices extraídos e testados, com menor custo de continuidade;
- contrato REST já iniciado e operacional.

## 6. Backlog executável da Etapa 4 (pagamentos)

### 6.1 Tarefas priorizadas (ordem de execução)

1. Consolidar remanescentes de `pagamentos/views.py` em adapters finos por endpoint.
2. Unificar políticas de erro HTTP por endpoint (webhook/status/relatórios/checkout) em `interfaces`.
3. Completar exemplos canônicos de sucesso/erro no OpenAPI para endpoints já expostos.
4. Reforçar cobertura de regressão por fluxo de checkout (pix/faturamento/retorno/status/webhook).
5. Padronizar logging de eventos críticos de pagamento/auditoria em adapter único.

### 6.2 Critério de aceite por tarefa

1. Sem regra de negócio nova em `views.py`; somente orquestração HTTP.
2. Respostas de erro/sucesso mapeadas centralmente e reutilizadas.
3. OpenAPI válido com exemplos úteis e alinhado ao comportamento real.
4. Smoke dirigido por fluxo + `tests/pagamentos` verde.
5. Eventos críticos registrados de forma consistente e verificável em teste.

### 6.3 Rollback local por tarefa (sem Git)

1. Copiar arquivo alterado para `.bak` antes de patch.
2. Se regressão, restaurar `.bak` e rerodar smoke do fluxo afetado.
3. Se migrar schema/contrato, validar parse YAML e testes focados antes de manter.

## 7. Checklist de prontidão (início imediato Etapa 4)

- Ambiente local e venv operacionais
- `manage.py check` verde
- `tests/accounts` estável (baseline do piloto)
- OpenAPI carregando sem erro
- roteiro de smoke por fluxo de pagamentos disponível
- documentação de progresso/handoff atualizada

## 8. Próximas ações (24-48h)

1. Executar tarefa 6.1 (extrações remanescentes em `pagamentos/views.py`) com smoke imediato.
2. Aplicar tarefa 6.2 (interfaces de resposta HTTP de pagamentos).
3. Atualizar OpenAPI com exemplos (tarefa 6.3) e validar parse.
4. Rodar suíte focada de pagamentos e registrar handoff incremental.

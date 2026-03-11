# Onda 2 - Fechamento Executivo

Data: 2026-03-10

## Status geral
- Onda 2 executada de forma incremental com validacao continua por teste automatizado e smoke funcional.
- Evidencias registradas em:
  - `docs/etapas/smoke_onda2_*.md` (20 arquivos)
  - `docs/etapas/onda2_iteracao_*.md` (17 arquivos)
- Ultima validacao consolidada:
  - `.\.venv\Scripts\python.exe manage.py check` OK
  - Suite direcionada Onda 2: 129 passed, 4 warnings

## Cobertura por modulo (camada application)

| Modulo | Arquivos application (sem __init__) | Status Onda 2 |
|---|---:|---|
| `eventos` | 16 | Consolidado (principal foco da onda) |
| `accounts` | 2 | Consolidado na onda |
| `tokens` | 2 | Consolidado na onda |
| `pagamentos` | 2 | Consolidado na onda |
| `organizacoes` | 1 | Consolidado na onda |
| `nucleos` | 1 | Consolidado na onda |
| `ai_chat` | 0 | Pendente |
| `audit` | 0 | Pendente |
| `conexoes` | 0 | Pendente |
| `configuracoes` | 0 | Pendente |
| `dashboard` | 0 | Pendente |
| `feed` | 0 | Pendente |
| `membros` | 0 | Pendente |
| `notificacoes` | 0 | Pendente |
| `portfolio` | 0 | Pendente (dominio dedicado) |
| `webhooks` | 0 | Pendente |

## Entregas relevantes da Onda 2
- Extracoes de regras de negocio e fluxo em `eventos`:
  - checkout, check-in, convites, briefing, orcamento, listagem por dia, feedback/inscritos
  - contexto do detalhe do evento e contexto de portfolio
  - politicas de escrita (create/update/delete) e inscricao management
- Extracoes complementares em modulos base:
  - `accounts`: navegacao/autorizacao de perfil
  - `tokens`: fluxo de convite e validacao de token
  - `pagamentos`: mapeamento de transacao e resolucao de organizacao
  - `organizacoes`/`nucleos`: politicas de acesso/visibilidade
- Correcoes oportunisticas identificadas por smoke:
  - multiplos templates com `{% static %}` sem `{% load static %}`
  - fallback de navegacao em portfolio sem dependencia de `HTTP_REFERER`

## Riscos residuais (prioridade)
1. `P1 - Cobertura funcional incompleta fora do eixo eventos`:
   - modulos com estrutura criada, mas sem extracoes efetivas (`ai_chat`, `notificacoes`, `webhooks`, etc.).
2. `P1 - Regressao de template em views menos exercitadas`:
   - padrao recorrente de erros de template detectado por smoke.
3. `P2 - Acoplamento remanescente em views monoliticas`:
   - embora reduzido, ainda existem blocos grandes em views legadas fora do escopo ja extraido.
4. `P2 - Testes de integracao E2E por dominio`:
   - boa cobertura unitaria de application, mas com espaco para cenarios integrados por modulo.

## Trade-offs aplicados na Onda 2
- Priorizacao de extracao de regras com maior risco de negocio (`eventos` + `pagamentos`) antes de satelites.
- Correcoes de template foram feitas durante smoke para manter fluxo executavel, mesmo nao sendo o foco primario de arquitetura.
- Sem Git/branching: rollback controlado via roteiro de smoke (post apply/post rollback) e validacao imediata.

## Backlog recomendado para Onda 3

### Onda 3.1 (base operacional / plataforma)
1. `notificacoes`: extrair regras de template de mensagem e politicas de envio.
2. `webhooks`: consolidar validacao de origem, assinatura e roteamento de eventos.
3. `audit`: padronizar eventos de auditoria em application + infraestrutura de persistencia.

### Onda 3.2 (dominios de negocio satelite)
1. `membros`: politicas de vinculo, status e autorizacao de operacoes.
2. `conexoes` e `feed`: extracao de regras de timeline/interacao.
3. `dashboard`: montagem de agregados e metricas em application.

### Onda 3.3 (integracoes e modulos especializados)
1. `ai_chat`: regras de prompt/contexto e politicas de acesso por organizacao.
2. `configuracoes`: normalizacao de defaults e override por organizacao.
3. `portfolio` (modulo dedicado): separar o que ainda depende de `eventos` para dominio proprio.

## Critério de pronto para iniciar Onda 3
- Manter disciplina atual:
  - cada slice com extracao + testes + smoke + documento de iteracao
  - rollback local explicito quando houver mutacao de dados
- Preservar contrato REST atual (OpenAPI) sem ampliar escopo para real-time/WS nesta fase.

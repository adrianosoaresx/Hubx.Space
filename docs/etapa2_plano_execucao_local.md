# Etapa 2 - Plano de Execucao Local (Sem Git)

Data de referencia: 10/03/2026  
Escopo: reorganizacao arquitetural incremental do Hubx em copia local.

## 1) Decisoes fechadas

- Frontend Next.js nao sera mantido como produto paralelo.
- Modulos legados `financeiro` e `associados` devem ser excluidos do sistema.
- Prioridade de negocio na Onda 2: `eventos` antes de `pagamentos`.
- `OpenAPI` cobre apenas contratos REST nesta fase.

## 2) Pre-flight obrigatorio

Executar antes de qualquer alteracao estrutural:

1. Criar pasta de backup local com timestamp.
2. Copiar codigo completo para backup.
3. Copiar `db.sqlite3` para backup.
4. Registrar checklist de baseline (smoke manual):
   - login/logout
   - perfil
   - listagem de nucleos
   - listagem de eventos
   - checkout de inscricao (fluxo principal)

Exemplo PowerShell:

```powershell
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$backupRoot = "X:\Projeto\Hubx.Space_backup\$ts"
New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
robocopy "X:\Projeto\Hubx.Space" "$backupRoot\Hubx.Space" /MIR /XD .venv node_modules .git .pytest_cache .ruff_cache __pycache__
Copy-Item "X:\Projeto\Hubx.Space\db.sqlite3" "$backupRoot\db.sqlite3" -Force
```

## 3) Onda 1 - Base/plataforma (ordem fixa)

### T1. Estrutura alvo monorepo local
- Criar:
  - `apps/backend/app/modules/`
  - `apps/frontend/templates/`
  - `apps/frontend/static/{css,js,img}`
  - `packages/contracts/`
  - `docs/etapas/`
- Aceite:
  - Estrutura criada e versionada localmente.
- Rollback:
  - Remover as novas pastas e restaurar backup.

### T2. Esqueleto de todos os modulos
- Para cada modulo identificado, criar:
  - `domain/`
  - `application/`
  - `infrastructure/`
  - `interfaces/`
- Lista minima:
  - `core, accounts, tokens, conexoes, portfolio, organizacoes, nucleos, membros, eventos, pagamentos, feed, notificacoes, configuracoes, dashboard, ai_chat, audit, webhooks`
- Aceite:
  - 100% dos modulos com estrutura-base criada.
- Rollback:
  - Restaurar apenas `apps/backend/app/modules/`.

### T3. Contrato OpenAPI inicial (REST only)
- Criar `packages/contracts/openapi.yaml`.
- Cobrir inicialmente endpoints REST dos apps com `api_urls.py` e APIs REST em `pagamentos`.
- Aceite:
  - Arquivo valido e revisavel; inclui recursos REST criticos (`accounts, tokens, organizacoes, nucleos, eventos, feed, notificacoes, configuracoes, ai_chat, audit`).
- Rollback:
  - Restaurar arquivo de backup anterior.

### T4. Hardening de configuracao
- Remover credenciais hardcoded de `Hubx/settings.py`.
- Forcar leitura de segredos por variavel de ambiente.
- Aceite:
  - Nenhum segredo sensivel fixo em codigo.
- Rollback:
  - Restaurar `Hubx/settings.py` + `.env` a partir do backup.

### T5. Exclusao segura de componentes descontinuados

#### T5.1 Frontend Next.js
- Remover:
  - `app/`, `components/`, `hooks/`, `lib/`
  - `next.config.mjs`, `tsconfig.json`, `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `postcss.config.mjs`, `tailwind.config.ts` (avaliar dependencia do tailwind Django antes de remover este arquivo)
- Ajustar docs e scripts que citam `npm run dev/build/start`.
- Aceite:
  - Projeto Django sobe sem dependencia do Next.
- Rollback:
  - Restaurar arquivos removidos a partir do backup.

#### T5.2 Legados `financeiro` e `associados`
- Remover pastas:
  - `financeiro/`
  - `associados/`
- Buscar e limpar referencias residuais em `*.py`, `*.html`, `*.md`.
- Aceite:
  - Nenhuma referencia de import/URL/settings para modulos excluidos.
- Rollback:
  - Restaurar pastas removidas e DB do snapshot.

## 4) Onda 2 - Core de negocio (prioridade definida)

Ordem obrigatoria:

1. `accounts`
2. `tokens`
3. `organizacoes`
4. `nucleos`
5. `eventos`  <- prioridade antes de pagamentos
6. `pagamentos`
7. `feed`

Regra de execucao por modulo:

1. Criar DTOs e casos de uso em `application`.
2. Mover regras puras para `domain`.
3. Isolar persistencia/gateways em `infrastructure`.
4. Manter endpoints/HTMX em `interfaces` com adapter fino.
5. Validar smoke do modulo.

Aceite por modulo:

- Fluxos web/HTMX do modulo funcionam como baseline.
- Endpoints REST do modulo continuam respondendo.
- `views.py` reduz concentracao de regra de negocio.
- Casos de uso criticos testados localmente.

Rollback por modulo:

- Restaurar pasta do modulo + `db.sqlite3` do snapshot anterior ao modulo.

## 5) Onda 3 - Satelites e integracoes

Modulos:

- `notificacoes, configuracoes, dashboard, conexoes, membros, portfolio, ai_chat, audit, webhooks`

Objetivo:

- Completar padrao de camadas.
- Isolar gateways externos.
- Eliminar acoplamentos restantes no fluxo HTTP.

Aceite:

- Sem regra de negocio critica em controllers/templates.
- Contratos REST atualizados no `openapi.yaml`.

Rollback:

- Restauracao por modulo a partir de backup incremental.

## 6) Matriz de dependencia critica

- `pagamentos` depende de `eventos` (inscricao, checkout, status).
- `nucleos` e `organizacoes` sustentam filtros e autorizacoes de `eventos` e `feed`.
- `tokens` e `accounts` sustentam identidade e seguranca transversal.

Conclusao operacional:

- Nao iniciar migracao de `pagamentos` antes de estabilizar `eventos`.

## 7) Checklist de inicio da implementacao

- Backup local completo criado e validado.
- Plano de rollback por modulo acordado.
- Estrutura alvo criada.
- OpenAPI REST inicial criado.
- Segredos retirados do codigo.
- Decisoes de exclusao (Next/financeiro/associados) aplicadas e validadas.
- Smoke baseline documentado.

## 8) Proxima janela (24-48h)

1. Executar Onda 1 completa.
2. Iniciar Onda 2 em `accounts` e `tokens`.
3. Preparar migracao de `organizacoes` e `nucleos`.
4. Reservar `eventos` como primeiro modulo de alta complexidade antes de `pagamentos`.


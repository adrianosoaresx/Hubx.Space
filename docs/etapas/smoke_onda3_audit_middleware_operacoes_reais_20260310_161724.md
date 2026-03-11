# Smoke Onda 3.1 - Audit Middleware em Operacoes Reais

Data: 2026-03-10 16:17:24
Usuario de negocio: id=3 username=daianygaspar email=daianygaspar@gmail.com user_type=nucleado organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Escopo: validacao de auditoria em caminhos reais prefixados por `/membros/` com normalizacao de status e sanitizacao de payload.

Sequencia executada:
1. Login de usuario de negocio com organizacao valida.
2. GET `/membros/` (resposta de permissao atual do perfil).
3. GET `/membros/inexistente/?token=s3cr3t&q=ok`.
4. Leitura dos dois logs mais recentes para as actions auditadas.

| Check | Path | Status | Observacao |
|---|---|---:|---|
| membros_list | `/membros/` | 403 | Recurso restrito ao perfil atual, auditoria deve registrar FAILURE |
| membros_inexistente | `/membros/inexistente/?token=s3cr3t&q=ok` | 404 | Rota inexistente, auditoria deve registrar FAILURE |

Resultado de auditoria:
- `AUDIT_COUNT`: before=1016, after=1018, delta=2
- Log 1: `action=GET:/membros/inexistente/`, `status=FAILURE`, `severity=high`, `has_token=False`, `keys=q,severity`
- Log 2: `action=GET:/membros/`, `status=FAILURE`, `severity=high`, `has_token=False`, `keys=severity`

Validacao chave:
- Campo sensivel `token` removido do metadata persistido.
- Severidade adicionada automaticamente em metadata (`severity=high` para falhas).

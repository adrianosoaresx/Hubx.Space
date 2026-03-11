# Smoke Onda 3.2 - Membros Promotion Member State

Data: 2026-03-10 16:53:38
Usuario de negocio (admin): id=2 username=cdladmin user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Usuario alvo smoke: id=110 username=smoke_membro_state_2_1 organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Escopo: validar extração da atualização de estado final do membro para `application`.

| Check | Path | Status | Observacao |
|---|---|---:|---|
| membros_promover_form_get | `/membros/110/promover/form/` | 200 | Usuário de negócio com permissões/organização válidas |
| membros_promover_associado_post | `/membros/110/promover/form/` | 200 | Fluxo de convidado para associado executado |
| membros_promover_associado_estado | `User(id=110)` | OK | `user_type=associado`, `is_associado=True`, `is_coordenador=False`, `nucleo=None` |
| membros_promover_associado_participacoes | `ParticipacaoNucleo(user=110)` | OK | `participacoes_ativas=0` |

Comando executado:
- `./.venv/Scripts/python.exe manage.py shell -c "<script smoke promotion member state>"`

Validação chave:
- A atualização pós-persistência foi aplicada via `application` sem regressão do fluxo HTTP.

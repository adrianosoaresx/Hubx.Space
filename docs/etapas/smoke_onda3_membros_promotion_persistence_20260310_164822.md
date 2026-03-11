# Smoke Onda 3.2 - Membros Promotion Persistence

Data: 2026-03-10 16:48:22
Usuario de negocio (admin): id=2 username=cdladmin user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Usuario alvo smoke: id=109 username=smoke_membro_persist_2_1 user_type=convidado organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Nucleo de teste: id=1 nome=Núcleo da Mulher organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Escopo: validar extração da persistência transacional de promoção para `application`.

| Check | Path | Status | Observacao |
|---|---|---:|---|
| membros_promover_form_get | `/membros/109/promover/form/` | 200 | Usuário de negócio com organização válida acessa formulário |
| membros_promover_conflict_post | `/membros/109/promover/form/` | 400 | Conflito de promover/remover nucleado no mesmo núcleo bloqueado |
| membros_promover_conflict_no_mutation | `/membros/109/promover/form/` | OK | `participacao_delta=0` no cenário inválido |
| membros_promover_valid_post | `/membros/109/promover/form/` | 200 | Promoção válida aplicada via serviço de persistência |
| membros_promover_valid_participacao | `ParticipacaoNucleo(user=109,nucleo=1)` | OK | `status=ativo`, `papel=membro`, `status_suspensao=False` |

Comando executado:
- `./.venv/Scripts/python.exe manage.py shell -c "<script smoke promotion persistence>"`

Validação chave:
- Fluxo inválido continua sem mutação.
- Fluxo válido cria/atualiza participação corretamente após extração para `apps.backend...application.promotion_persistence`.

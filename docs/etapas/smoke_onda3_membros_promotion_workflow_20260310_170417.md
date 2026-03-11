# Smoke Onda 3.2 - Membros Promotion Workflow

Data: 2026-03-10 17:04:17
Usuario de negocio (admin): id=2 username=cdladmin user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Usuario alvo smoke: id=111 username=smoke_membro_workflow_2_1 organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Nucleo de teste: id=1 nome=Núcleo da Mulher organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Escopo: validar extração do comando completo de promoção para `application`.

| Check | Path | Status | Observacao |
|---|---|---:|---|
| membros_promover_form_get | `/membros/111/promover/form/` | 200 | Formulário acessível com permissões válidas |
| membros_promover_invalid_coord_sem_papel | `/membros/111/promover/form/` | 400 | Erro de validação preservado no use-case central |
| membros_promover_invalid_selected_preserved | `/membros/111/promover/form/` | OK | `selected_coordenador=['1']` mantido |
| membros_promover_valid_nucleado | `/membros/111/promover/form/` | 200 | Promoção aplicada via workflow unificado |
| membros_promover_valid_estado | `User(id=111)` | OK | `user_type=nucleado`, `is_associado=True`, `nucleo=1` |
| membros_promover_valid_participacao | `ParticipacaoNucleo(user=111,nucleo=1)` | OK | `status=ativo`, `papel=membro`, `status_suspensao=False` |

Comando executado:
- `./.venv/Scripts/python.exe manage.py shell -c "<script smoke promotion workflow>"`

Validação chave:
- View passou a atuar como adapter HTTP/HTMX, com validação + persistência + sync centralizados em `application.promotion_workflow`.

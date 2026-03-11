# Smoke Onda 3.2 - Membros Promotion Selection Parsing

Data: 2026-03-10 16:36:38
Usuario de negocio (admin): id=2 username=cdladmin email=cdladmin@hubx.local user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Usuario alvo: id=3 username=daianygaspar email=daianygaspar@gmail.com user_type=nucleado organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Nucleo de teste: id=1 nome=Núcleo da Mulher organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Escopo: validar parsing/composição de seleção de promoção após extração para `application`.

| Check | Path | Status | Observacao |
|---|---|---:|---|
| membros_promover_form_get | `/membros/3/promover/form/` | 200 | Formulário disponível para admin da organização |
| membros_promover_conflict_post | `/membros/3/promover/form/` | 400 | Conflito promover/remover no mesmo núcleo; `participacao_delta=0` |
| membros_promover_coord_sem_papel | `/membros/3/promover/form/` | 400 | Coordenação sem papel rejeitada corretamente |

Comando executado:
- `./.venv/Scripts/python.exe manage.py shell -c "... smoke promotion selection ..."`

Validação chave:
- Parsing de IDs e papéis mantém comportamento funcional anterior.
- Cenários inválidos continuam bloqueados sem mutação indevida de participação.

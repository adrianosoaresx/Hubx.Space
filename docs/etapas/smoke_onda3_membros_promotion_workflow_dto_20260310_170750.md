# Smoke Onda 3.2 - Membros Promotion Workflow DTO

Data: 2026-03-10 17:07:50
Usuario de negocio (admin): id=2 username=cdladmin user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Usuario alvo smoke: id=112 username=smoke_membro_dto_2_1 organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Nucleo de teste: id=1 nome=Núcleo da Mulher organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Escopo: validar compatibilidade do adapter HTTP após padronização de DTO interno no workflow de promoção.

| Check | Path | Status | Observacao |
|---|---|---:|---|
| membros_promover_form_get | `/membros/112/promover/form/` | 200 | Formulário acessível com permissões válidas |
| membros_promover_invalid_coord_sem_papel | `/membros/112/promover/form/` | 400 | Validação de coordenação sem papel permanece ativa |
| membros_promover_valid_nucleado | `/membros/112/promover/form/` | 200 | Fluxo válido processado com DTO interno |
| membros_promover_valid_estado | `User(id=112)` | OK | `user_type=nucleado`, `is_associado=True`, `is_coordenador=False` |
| membros_promover_valid_participacao | `ParticipacaoNucleo(user=112,nucleo=1)` | OK | `status=ativo`, `papel=membro`, `status_suspensao=False` |

Comando executado:
- `./.venv/Scripts/python.exe manage.py shell -c "<script smoke promotion workflow dto>"`

Validação chave:
- A camada HTTP continua estável enquanto o caso de uso passa a operar com contrato interno explícito.

# Smoke Onda 3.2 - Membros Promocao Conflict Validation

Data: 2026-03-10 16:32:56
Usuario de negocio (admin): id=2 username=cdladmin email=cdladmin@hubx.local user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Usuario alvo: id=3 username=daianygaspar email=daianygaspar@gmail.com user_type=nucleado organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Nucleo de teste: id=1 nome=Núcleo da Mulher organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Escopo: validar conflito de promoção/remoção no mesmo núcleo após extração das regras para `application`.

| Check | Path | Status | Observacao |
|---|---|---:|---|
| membros_promover_form_get | `/membros/3/promover/form/` | 200 | Formulário carregado com permissões válidas |
| membros_promover_conflict_post | `/membros/3/promover/form/` | 400 | Conflito detectado (`promover/remover` no mesmo núcleo), `participacao_delta=0` |

Comando executado:
- `./.venv/Scripts/python.exe manage.py shell -c "... smoke conflito promocao ..."`

Validacao chave:
- A regra de conflito foi aplicada corretamente via camada `application`.
- Sem mutação indevida de participação no cenário inválido.

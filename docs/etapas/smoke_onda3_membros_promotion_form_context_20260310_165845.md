# Smoke Onda 3.2 - Membros Promotion Form Context

Data: 2026-03-10 16:58:45
Usuario de negocio (admin): id=2 username=cdladmin user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Usuario alvo: id=3 username=daianygaspar user_type=nucleado organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Nucleo de teste: id=1 nome=Núcleo da Mulher organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Escopo: validar extração do contexto de tela de promoção para `application`.

| Check | Path | Status | Observacao |
|---|---|---:|---|
| membros_promover_form_get | `/membros/3/promover/form/?section=nucleados` | 200 | Formulário renderizado com contexto completo |
| membros_promover_form_origin_section | `/membros/3/promover/form/?section=nucleados` | OK | `origin_section=nucleados` preservado |
| membros_promover_form_context_nucleos | `/membros/3/promover/form/?section=nucleados` | OK | `nucleos_count=2`, `coordenador_role_choices` presente |
| membros_promover_form_invalid_post | `/membros/3/promover/form/` | 400 | Coordenação sem papel retorna erro esperado |
| membros_promover_form_invalid_selected | `/membros/3/promover/form/` | OK | `selected_coordenador=['1']` mantido no contexto |

Comando executado:
- `./.venv/Scripts/python.exe manage.py shell -c "<script smoke promotion form context>"`

Validação chave:
- Contexto da tela foi preservado após extração para `application`, incluindo filtros de origem e estado de seleção em erro.

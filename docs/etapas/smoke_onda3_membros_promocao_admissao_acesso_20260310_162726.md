# Smoke Onda 3.2 - Membros Promocao e Admissao (Acesso)

Data: 2026-03-10 16:27:26
Usuario de negocio (admin): id=2 username=cdladmin email=cdladmin@hubx.local user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Usuario alvo para promocao: id=3 username=daianygaspar email=daianygaspar@gmail.com user_type=nucleado organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Escopo: validar acesso aos fluxos de membros com permissao/organizacao validas (listagem, promocao e admissao).

| Check | Path | Status | Observacao |
|---|---|---:|---|
| perfil_admin | `/accounts/perfil/` | 200 | Usuario autenticado com perfil admin da organizacao |
| membros_list | `/membros/` | 200 | Listagem de membros carregada |
| membros_promover_list | `/membros/promover/` | 200 | Tela de promocao acessivel |
| membros_promover_form | `/membros/3/promover/form/` | 200 | Formulario de promocao do alvo carregado |
| membros_adicionar_associado_get | `/membros/novo/?tipo=associado` | 200 | Tela de admissao com tipo permitido |
| membros_promover_carousel_api | `/membros/promover/carousel/?page=1` | 200 | API HTMX de carrossel de promocao funcional |

Comando executado:
- `./.venv/Scripts/python.exe manage.py shell -c "... smoke membros ..."`

Notas:
- Smoke focado em acesso e carregamento de telas/partials sem mutacao de dados.
- Usuario e alvo pertencem a mesma organizacao, garantindo validade de escopo.

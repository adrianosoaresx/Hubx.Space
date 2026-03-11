# Smoke Onda 3.4 - Hardening Conexoes Paginacao

Data: 2026-03-10 17:36:19
Usuario de negocio (admin): id=2 username=cdladmin user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Escopo: validar estabilização de paginação de conexões após ordenação explícita do queryset.

| Check | Path | Status | Observacao |
|---|---|---:|---|
| conexoes_perfil_sections_get | `/conexoes/perfil/sections/conexoes/` | 200 | Seção de conexões renderizada com usuário de negócio válido |
| conexoes_perfil_sections_cards | `/conexoes/perfil/sections/conexoes/` | OK | Conteúdo contém `connection-card` |
| conexoes_perfil_sections_minhas | `/conexoes/perfil/sections/conexoes/` | OK | Conteúdo contém seção `minhas` |

Comando executado:
- `./.venv/Scripts/python.exe manage.py shell -c "<script smoke hardening conexoes>"`

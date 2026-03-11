# Smoke Onda 3.1 - Notificacoes Dropdown e Lista

Data: 2026-03-10 15:52:04
Usuario de negocio: id=3 username=daianygaspar email=daianygaspar@gmail.com user_type=nucleado organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Escopo: validacao de fluxo web de notificacoes com usuario autenticado e organizacao valida.

Preparacao:
- Garantido template `feed_like` ativo.
- Criado NotificationLog `app/enviada` para popular lista/dropdown.

| Check | Path | Status | Observacao |
|---|---|---:|---|
| perfil_negocio | `/accounts/perfil/` | 200 | Sessao autenticada valida |
| notificacoes_list | `/notificacoes/minhas/` | 200 | Tela carregada apos correcao de template static |
| notificacoes_count | `/notificacoes/minhas/contagem/` | 200 | Badge de pendencias renderizada |
| notificacoes_dropdown | `/notificacoes/minhas/dropdown/` | 200 | Dropdown HTMX com links de destino resolvidos |

Comando executado:
- `./.venv/Scripts/python.exe manage.py shell -c "... smoke notificacoes ..."`

Incidente encontrado e corrigido durante smoke:
- `TemplateSyntaxError` em `notificacoes/notificacoes_list.html` por uso de `{% static %}` sem `{% load static %}`.
- Correcao aplicada e smoke reexecutado com sucesso.

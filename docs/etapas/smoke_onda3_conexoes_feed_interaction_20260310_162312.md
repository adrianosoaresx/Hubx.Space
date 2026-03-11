# Smoke Onda 3.1 - Conexoes e Feed Interaction

Data: 2026-03-10 16:23:12
Usuario de negocio: id=3 username=daianygaspar email=daianygaspar@gmail.com user_type=nucleado organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Usuario alvo (peer): id=2 username=cdladmin email=cdladmin@hubx.local user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Escopo: validar fluxo cruzado de conexoes + notificacao de interacao no feed com contexto normalizado.

| Check | Path | Status | Observacao |
|---|---|---:|---|
| perfil_negocio | `/accounts/perfil/` | 200 | Sessao autenticada valida |
| conexoes_dashboard | `/conexoes/perfil/sections/conexoes/` | 200 | Dashboard de conexoes carregado |
| conexoes_solicitar | `/conexoes/perfil/conexoes/2/solicitar/` | 302 | Solicitacao criada e redirecionada para busca |
| feed_list | `/feed/` | 200 | Lista de feed acessivel para usuario de negocio |
| feed_interaction_notify_task | `feed.tasks.notificar_autor_sobre_interacao` | 200 | Task executada diretamente, `logs_delta=1` para autor do post |

Validacao de notificacao cruzada:
- Template de interacao resolvido corretamente para `like`.
- Contexto de notificacao inclui `post_id` e `interaction_type`.
- `NotificationLog` incrementado para o autor do post.

Notas:
- O envio assíncrono de conexoes foi agendado sem erro via task Celery (`enviar_notificacao_conexao_async.delay`).
- Warning conhecido mantido: `UnorderedObjectListWarning` em paginação de conexoes (fora do escopo deste slice).

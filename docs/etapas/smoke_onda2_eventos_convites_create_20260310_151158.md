# Smoke Onda 2 - Eventos Convites Create

Data: 2026-03-10 15:11:58
Usuario: id=2 username=cdladmin email=cdladmin@hubx.local user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Evento alvo: id=65db8188-5715-4a8b-ac54-0a002e978c20 slug=evento-para-testes
Convite alvo: id=4 short_code=8L5ktZHUpA

| Check | Path | Status | Redirect/Obs |
|---|---|---:|---|
| perfil | `/accounts/perfil/` | 200 | `` |
| evento_detalhe | `/eventos/evento/65db8188-5715-4a8b-ac54-0a002e978c20/` | 200 | `` |
| convite_create_get | `/eventos/evento/65db8188-5715-4a8b-ac54-0a002e978c20/convites/novo/` | 200 | `` |
| convite_public_get | `/eventos/c/8L5ktZHUpA/` | 200 | `` |
| convite_public_post_existing_email | `/eventos/c/8L5ktZHUpA/` | 302 | `/accounts/login/?next=%2Feventos%2Fevento%2F65db8188-5715-4a8b-ac54-0a002e978c20%2Finscricao%2Foverview%2F` |

## Achados durante o smoke
- O fluxo inicialmente falhou por `TemplateSyntaxError` em template de convite com uso de `{% static %}` sem `{% load static %}`.
- Correcao aplicada:
  - `eventos/templates/eventos/convites/form.html`
- Reexecucao apos correcao: smoke 100% OK.

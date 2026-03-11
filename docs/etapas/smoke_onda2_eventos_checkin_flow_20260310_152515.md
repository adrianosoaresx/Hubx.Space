# Smoke Onda 2 - Eventos Checkin Flow

Data: 2026-03-10 15:25:15
Usuario: id=2 username=cdladmin email=cdladmin@hubx.local user_type=admin organizacao_id=dc8f57f1-4218-4ca5-ab37-3f11540c87bc
Inscricao alvo: id=10 uuid=093ab730-00e8-4452-ae38-291b2df37c23 evento=65db8188-5715-4a8b-ac54-0a002e978c20 user=107
Check-in inicial/final: True -> True

| Check | Path | Status | Redirect/Obs |
|---|---|---:|---|
| perfil | `/accounts/perfil/` | 200 | `` |
| evento_detalhe | `/eventos/evento/65db8188-5715-4a8b-ac54-0a002e978c20/` | 200 | `` |
| checkin_form_get | `/eventos/checkin/10/` | 200 | `` |
| checkin_post_invalid | `/eventos/api/inscricoes/10/checkin/` | 400 | `` |
| checkin_post_valid | `/eventos/api/inscricoes/10/checkin/` | 200 | `{"status":"ok","message":"Check-in já realizado."}` |

## Observacao de rollback controlado
- O smoke utilizou inscricao com check-in ja realizado para evitar mutacao de estado.
- A validacao com codigo invalido retornou `400` conforme esperado, sem alterar estado da inscricao.

# Onda 2 - Iteracao Eventos Checkout Flow

Data: 2026-03-10 14:05:39

## Escopo executado
- Extracao de regras de checkout de eventos para camada `application`:
  - `apps/backend/app/modules/eventos/application/checkout_flow.py`
    - `build_checkout_profile_data`
    - `build_initial_checkout_data`
    - `is_evento_gratuito`
    - `is_checkout_required`
    - `resolve_metodo_pagamento`
- Delegacao de regras em `eventos/views.py`:
  - `InscricaoEventoPagamentoCreateView`
  - `InscricaoEventoCheckoutView`

## Beneficio
- Reducao de duplicacao de regra entre dois fluxos de inscricao/checkout.
- Regras de decisao de checkout agora testaveis de forma isolada.

## Testes adicionados
- `tests/eventos/test_eventos_application_checkout_flow.py`

## Validacao
- `python manage.py check` OK
- Suite direcionada Onda 2: 41 passed, 3 warnings
- Smoke funcional com usuario de negocio e organizacao valida:
  - `docs/etapas/smoke_onda2_eventos_checkout_20260310_140516.md`

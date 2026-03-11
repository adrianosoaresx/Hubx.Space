# Onda 2 - Iteracao Pagamentos e Eventos

Data: 2026-03-10 13:51:41

## Escopo executado
- Extracao inicial de regras de pagamentos para camada pplication:
  - 	ransaction_mapping.py:
    - mapear_status_pagamento
    - 
ormalizar_uuid
  - organization_resolution.py:
    - obter_organizacao_checkout
    - obter_organizacao_webhook
- Delegacao de pagamentos/views.py para os novos casos de uso de aplicacao.
- Extracao inicial de regras de visibilidade de ventos para camada pplication:
  - isibility.py:
    - get_tipo_usuario
    - is_guest_user
    - get_nucleos_coordenacao_consultoria_ids
    - esolve_planejamento_permissions
- Delegacao de ventos/views.py para os novos casos de uso de aplicacao.

## Testes adicionados
- 	ests/pagamentos/test_application_transaction_mapping.py
- 	ests/pagamentos/test_application_organization_resolution.py
- 	ests/eventos/test_eventos_application_visibility.py

## Validacao tecnica
- manage.py check: OK
- Suite direcionada Onda 2 (accounts/tokens/organizacoes/nucleos/pagamentos/eventos): 33 passed
- Warnings: 3 (deprecations Django 6.0, sem regressao funcional)

## Observacoes
- Ambiente Python correto para os smokes e checks: .venv\\Scripts\\python.exe.
- Priorizacao de negocio mantida nesta iteracao: pagamentos e ventos tratados antes de avancar para outros satelites.

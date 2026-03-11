from __future__ import annotations

import time

from django.db import OperationalError


class DjangoPaymentConfirmationGateway:
    def __init__(self, *, payment_model_getter, status_mapper, logger) -> None:
        self._payment_model_getter = payment_model_getter
        self._status_mapper = status_mapper
        self._logger = logger

    def confirm_with_retry(self, *, service, transacao, retry_delays: tuple[float, ...]) -> None:
        last_error: Exception | None = None
        for tentativa, delay in enumerate(retry_delays, start=1):
            if delay:
                time.sleep(delay)
            try:
                service.confirmar_pagamento(transacao)
                return
            except OperationalError as exc:
                last_error = exc
                self._logger.warning(
                    "confirmar_pagamento_operational_error",
                    extra={"transacao_id": transacao.id, "tentativa": tentativa},
                )
        if last_error:
            raise last_error

    def sync_payment_model(self, *, transacao) -> None:
        payment_id = (transacao.detalhes or {}).get("payment_id")
        if not payment_id:
            return

        payment_model = self._payment_model_getter()
        pagamento = payment_model.objects.filter(pk=payment_id).first()
        if not pagamento:
            return

        status_mapeado = self._status_mapper(pagamento.status)
        atualizacoes: list[str] = []
        if transacao.status != status_mapeado:
            transacao.status = status_mapeado
            atualizacoes.append("status")
        if pagamento.transaction_id and transacao.external_id != pagamento.transaction_id:
            transacao.external_id = pagamento.transaction_id
            atualizacoes.append("external_id")

        detalhes = transacao.detalhes or {}
        detalhes.update({"payment_status": pagamento.status, "payment_token": pagamento.token})
        transacao.detalhes = detalhes
        atualizacoes.append("detalhes")

        if atualizacoes:
            transacao.save(update_fields=list(dict.fromkeys([*atualizacoes, "atualizado_em"])))

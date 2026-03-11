from __future__ import annotations

import logging
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt

from drf_spectacular.utils import OpenApiResponse, extend_schema
from payments import get_payment_model
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.views import APIView

from eventos.models import InscricaoEvento
from organizacoes.models import Organizacao
from pagamentos.forms import FaturamentoForm, PixCheckoutForm
from pagamentos.models import Transacao
from pagamentos.providers import MercadoPagoProvider, PayPalProvider
from pagamentos.serializers import CheckoutResponseSerializer, CheckoutSerializer, WebhookSerializer
from pagamentos.services import PagamentoService
from apps.backend.app.modules.pagamentos.application.use_cases import (
    execute_payment_webhook_orchestration,
    build_transacoes_csv_content,
    build_faturamento_checkout_input,
    execute_faturamento_checkout_use_case,
    execute_pix_checkout_use_case,
    mapear_status_pagamento,
    normalizar_uuid,
    obter_organizacao_checkout,
    obter_organizacao_webhook,
    PaymentReturnContext,
    PaymentReturnUseCase,
    resolve_review_filter,
    TransacaoStatusUseCase,
)
from apps.backend.app.modules.pagamentos.application.checkout_inscricao_flow import (
    build_checkout_initial_from_inscricao,
)
from apps.backend.app.modules.pagamentos.infrastructure.payment_return_lookup import (
    DjangoPaymentReturnLookupRepository,
)
from apps.backend.app.modules.pagamentos.infrastructure.transacao_status_lookup import (
    DjangoTransacaoStatusLookupRepository,
)
from apps.backend.app.modules.pagamentos.infrastructure.transacao_reporting_lookup import (
    DjangoTransacaoReportingLookupRepository,
)
from apps.backend.app.modules.pagamentos.infrastructure.checkout_inscricao_repository import (
    DjangoCheckoutInscricaoRepository,
)
from apps.backend.app.modules.pagamentos.infrastructure.payment_confirmation_gateway import (
    DjangoPaymentConfirmationGateway,
)
from apps.backend.app.modules.pagamentos.interfaces.http_responses import (
    build_hx_redirect_response,
    build_invalid_return_status_response,
    build_invalid_transaction_response,
    build_payment_return_message,
    build_webhook_invalid_signature_response,
    build_webhook_missing_external_id_response,
    build_webhook_processed_response,
)
from apps.backend.app.modules.pagamentos.interfaces.checkout_http import (
    build_checkout_result_redirect_url,
    build_faturamento_checkout_context,
    build_pix_checkout_context,
    checkout_form_error_status,
)
from apps.backend.app.modules.pagamentos.interfaces.reporting_http import (
    build_transacao_revisao_context,
    build_transacoes_csv_response,
)
from apps.backend.app.modules.eventos.application.inscricao_result import (
    build_inscricao_result_context,
)
from apps.backend.app.modules.webhooks.application.payment_webhook_flow import (
    extract_external_id,
    parse_webhook_payload,
    resolve_signature_secret,
    validate_hmac_signature,
)
from apps.backend.app.modules.webhooks.application.payment_webhook_processing import (
    atualizar_inscricao_transacao_aprovada,
    confirm_known_transaction,
    find_transaction_by_external_id,
)

logger = logging.getLogger(__name__)

_payment_return_uc = PaymentReturnUseCase(
    lookup_repository=DjangoPaymentReturnLookupRepository(),
)
_checkout_inscricao_repository = DjangoCheckoutInscricaoRepository()
_transacao_status_uc = TransacaoStatusUseCase()
_transacao_status_lookup = DjangoTransacaoStatusLookupRepository()
_transacao_reporting_lookup = DjangoTransacaoReportingLookupRepository()
_payment_confirmation_gateway = DjangoPaymentConfirmationGateway(
    payment_model_getter=get_payment_model,
    status_mapper=mapear_status_pagamento,
    logger=logger,
)

class CheckoutBaseMixin:
    def _registrar_faturamento_inscricao(
        self,
        request: HttpRequest,
        inscricao_uuid: str | UUID | None,
        condicao_faturamento: str | None,
    ) -> InscricaoEvento | None:
        if not condicao_faturamento:
            return None
        normalized_uuid = str(inscricao_uuid or "").strip()
        inscricao = _checkout_inscricao_repository.find_accessible_inscricao(
            inscricao_uuid=normalized_uuid,
            user=request.user,
            include_deleted=True,
        )
        if not inscricao:
            logger.warning("checkout_inscricao_nao_encontrada", extra={"uuid": normalized_uuid})
            return None
        return _checkout_inscricao_repository.register_faturamento(
            inscricao=inscricao,
            condicao_faturamento=condicao_faturamento,
        )

    def _obter_organizacao(
        self, request: HttpRequest, organizacao_id: str | None = None
    ) -> Organizacao | None:
        return obter_organizacao_checkout(request=request, organizacao_id=organizacao_id)

    def _vincular_transacao_inscricao(
        self, request: HttpRequest, transacao: Transacao
    ) -> None:
        inscricao_uuid = self._normalizar_uuid(request.POST.get("inscricao_uuid"))
        inscricao = _checkout_inscricao_repository.find_accessible_inscricao(
            inscricao_uuid=inscricao_uuid,
            user=request.user,
            include_deleted=False,
        )
        if not inscricao:
            logger.warning("checkout_inscricao_nao_encontrada", extra={"uuid": inscricao_uuid})
            return

        _checkout_inscricao_repository.link_transacao(
            inscricao=inscricao,
            transacao=transacao,
        )

    @staticmethod
    def _normalizar_uuid(valor: Any):
        return normalizar_uuid(valor)


class PixCheckoutView(CheckoutBaseMixin, APIView):
    template_name = "pagamentos/pix_checkout.html"
    permission_classes = [AllowAny]

    @extend_schema(
        methods=["GET"],
        responses=OpenApiResponse(description="Página de checkout Pix"),
        tags=["Pagamentos"],
    )
    def get(self, request: HttpRequest) -> HttpResponse:
        organizacao = self._obter_organizacao(request)
        form = PixCheckoutForm(
            initial=self._get_initial_checkout(request),
            user=request.user,
            organizacao=organizacao,
        )
        provider = MercadoPagoProvider.from_organizacao(organizacao)
        return render(
            request,
            self.template_name,
            {"form": form, "provider_public_key": provider.public_key},
        )

    @extend_schema(
        methods=["POST"],
        request=CheckoutSerializer,
        responses={201: CheckoutResponseSerializer},
        tags=["Pagamentos"],
        description=_("Inicia o pagamento Pix no Mercado Pago e retorna a transação criada."),
    )
    def post(self, request: HttpRequest) -> HttpResponse:
        organizacao = self._obter_organizacao(request)
        form = PixCheckoutForm(request.POST, user=request.user, organizacao=organizacao)
        if not form.is_valid():
            logger.warning("checkout_form_invalido", extra={"errors": form.errors.as_json()})
            provider = MercadoPagoProvider.from_organizacao(organizacao)
            return render(
                request,
                self.template_name,
                build_pix_checkout_context(form=form, provider_public_key=provider.public_key),
                status=checkout_form_error_status(),
            )

        use_case_result = execute_pix_checkout_use_case(
            cleaned_data=form.cleaned_data,
            default_organizacao=organizacao,
            resolve_organizacao=lambda organizacao_id: self._obter_organizacao(
                request, organizacao_id
            ),
            vincular_transacao=lambda transacao: self._vincular_transacao_inscricao(
                request, transacao
            ),
        )
        if not use_case_result.success:
            form.add_error(None, use_case_result.error_message)
            return render(
                request,
                self.template_name,
                build_pix_checkout_context(
                    form=form,
                    provider_public_key=use_case_result.provider_public_key,
                ),
                status=checkout_form_error_status(),
            )

        return redirect(
            build_checkout_result_redirect_url(
                transacao_pk=use_case_result.transacao.pk,
            )
        )

    def _get_initial_checkout(self, request: HttpRequest) -> dict[str, Any]:
        initial: dict[str, Any] = {}
        inscricao_uuid = request.GET.get("inscricao_uuid")
        if inscricao_uuid:
            inscricao = _checkout_inscricao_repository.find_accessible_inscricao(
                inscricao_uuid=inscricao_uuid,
                user=request.user,
                include_deleted=True,
            )
            if inscricao:
                initial.update(
                    build_checkout_initial_from_inscricao(
                        inscricao=inscricao,
                        user=request.user,
                    )
                )
        return initial


class FaturamentoView(CheckoutBaseMixin, APIView):
    template_name = "pagamentos/faturamento_checkout.html"
    permission_classes = [AllowAny]

    @extend_schema(
        methods=["GET"],
        responses=OpenApiResponse(description="Página de faturamento interno"),
        tags=["Pagamentos"],
    )
    def get(self, request: HttpRequest) -> HttpResponse:
        organizacao = self._obter_organizacao(request)
        form = FaturamentoForm(initial=self._get_initial_faturamento(request), organizacao=organizacao)
        return render(request, self.template_name, {"form": form})

    @extend_schema(
        methods=["POST"],
        request=CheckoutSerializer,
        responses={201: CheckoutResponseSerializer},
        tags=["Pagamentos"],
        description=_("Registra o faturamento interno sem criar transação."),
    )
    def post(self, request: HttpRequest) -> HttpResponse:
        organizacao = self._obter_organizacao(request)
        form = FaturamentoForm(request.POST, organizacao=organizacao)
        if not form.is_valid():
            logger.warning("faturamento_form_invalido", extra={"errors": form.errors.as_json()})
            return render(
                request,
                self.template_name,
                build_faturamento_checkout_context(form=form),
                status=checkout_form_error_status(),
            )

        checkout_input = build_faturamento_checkout_input(cleaned_data=form.cleaned_data)
        use_case_result = execute_faturamento_checkout_use_case(
            checkout_input=checkout_input,
            registrar_faturamento=lambda inscricao_uuid, condicao_faturamento: self._registrar_faturamento_inscricao(
                request,
                inscricao_uuid=inscricao_uuid,
                condicao_faturamento=condicao_faturamento,
            ),
        )
        if not use_case_result.success:
            form.add_error(None, use_case_result.error_message)
            return render(
                request,
                self.template_name,
                build_faturamento_checkout_context(form=form),
                status=checkout_form_error_status(),
            )

        return redirect(use_case_result.redirect_url)

    def _get_initial_faturamento(self, request: HttpRequest) -> dict[str, Any]:
        initial: dict[str, Any] = {}
        inscricao_uuid = request.GET.get("inscricao_uuid")
        if inscricao_uuid:
            inscricao = _checkout_inscricao_repository.find_accessible_inscricao(
                inscricao_uuid=inscricao_uuid,
                user=request.user,
                include_deleted=True,
            )
            if inscricao:
                initial.update(
                    build_checkout_initial_from_inscricao(
                        inscricao=inscricao,
                        user=request.user,
                    )
                )
        return initial


class CheckoutResultadoView(APIView):
    permission_classes = [AllowAny]
    template_name = "pagamentos/checkout_resultado.html"

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        transacao = Transacao.objects.filter(pk=pk).first()
        return render(
            request,
            self.template_name,
            {"transacao": transacao, "form": PixCheckoutForm()},
        )


class ConfirmarPagamentoMixin:
    confirm_retry_delays = (0.0, 0.25, 0.5, 1.0)

    def _confirmar_pagamento_com_retry(
        self, service: PagamentoService, transacao: Transacao
    ) -> None:
        _payment_confirmation_gateway.confirm_with_retry(
            service=service,
            transacao=transacao,
            retry_delays=self.confirm_retry_delays,
        )

    def _sincronizar_pagamento_model(self, transacao: Transacao) -> None:
        _payment_confirmation_gateway.sync_payment_model(transacao=transacao)


class TransacaoStatusView(ConfirmarPagamentoMixin, APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["Pagamentos"], responses=CheckoutResponseSerializer)
    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        transacao = _transacao_status_lookup.get_transacao(pk=pk)
        if transacao is None:
            return build_invalid_transaction_response()

        inscricao = _transacao_status_lookup.get_inscricao_evento(transacao=transacao)
        decision = _transacao_status_uc.decide(
            status=transacao.status,
            has_inscricao=inscricao is not None,
            is_htmx_request=bool(request.headers.get("HX-Request")),
        )

        if decision.should_sync_payment_model:
            self._sincronizar_pagamento_model(transacao)
            inscricao = _transacao_status_lookup.get_inscricao_evento(transacao=transacao)
            decision = _transacao_status_uc.decide(
                status=transacao.status,
                has_inscricao=inscricao is not None,
                is_htmx_request=bool(request.headers.get("HX-Request")),
            )

        if decision.should_redirect_hx_to_inscricao and inscricao is not None:
            resultado_url = reverse("eventos:inscricao_resultado", kwargs={"uuid": inscricao.uuid})
            return build_hx_redirect_response(redirect_url=resultado_url)

        if decision.should_render_inscricao_result and inscricao is not None:
            contexto = self._montar_contexto_inscricao_resultado(request, inscricao)
            return render(request, "eventos/inscricoes/resultado.html", contexto)

        return render(
            request,
            "pagamentos/partials/checkout_resultado.html",
            {"transacao": transacao, "form": PixCheckoutForm()},
        )

    @staticmethod
    def _montar_contexto_inscricao_resultado(
        request: HttpRequest, inscricao: InscricaoEvento
    ) -> dict[str, Any]:
        return build_inscricao_result_context(
            request=request,
            inscricao=inscricao,
            status="success",
            message=None,
            title=_("Status da inscrição"),
        )


class MercadoPagoRetornoView(ConfirmarPagamentoMixin, APIView):
    permission_classes = [AllowAny]
    template_name = "pagamentos/retorno.html"

    def get(self, request: HttpRequest, status: str) -> HttpResponse:
        retorno_status = _payment_return_uc.resolve_status(raw_status=status)
        if retorno_status is None:
            return build_invalid_return_status_response()

        transacao = self._buscar_transacao(request)
        if transacao:
            self._sincronizar_pagamento_model(transacao)
        organizacao = getattr(getattr(transacao, "pedido", None), "organizacao", None)

        contexto = {
            "mensagem": self._mensagem(retorno_status, transacao is not None),
            "transacao": transacao,
            "form": PixCheckoutForm(organizacao=organizacao),
            "retorno_status": retorno_status,
        }
        return render(request, self.template_name, contexto)

    def _buscar_transacao(self, request: HttpRequest) -> Transacao | None:
        payment_token = request.GET.get("token") or request.GET.get("external_reference")
        payment_id = (
            request.GET.get("payment_id")
            or request.GET.get("collection_id")
            or request.GET.get("id")
        )
        return _payment_return_uc.find_transaction(
            payment_token=payment_token,
            payment_id=payment_id,
        )

    def _mensagem(self, status: str, possui_transacao: bool) -> str:
        message_key = _payment_return_uc.resolve_message(
            PaymentReturnContext(status=status, has_transaction=possui_transacao)
        )
        return build_payment_return_message(message_key=message_key)


@method_decorator(csrf_exempt, name="dispatch")
class WebhookView(ConfirmarPagamentoMixin, APIView):
    permission_classes = [AllowAny]
    authentication_classes: list[type] = []
    provider_class = MercadoPagoProvider
    signature_header_name = "X-Signature"
    signature_env_var = "MERCADO_PAGO_WEBHOOK_SECRET"
    organizacao_secret_attr = "mercado_pago_webhook_secret"

    @extend_schema(
        methods=["POST"],
        request=WebhookSerializer,
        responses={200: OpenApiResponse(description="Webhook processado")},
        tags=["Pagamentos"],
        description=_("Webhook de notificações do Mercado Pago com verificação de assinatura."),
    )
    def post(self, request: HttpRequest) -> HttpResponse:
        def _resolve_organizacao(payload: dict[str, Any], transacao: Transacao | None):
            return self._organizacao_from_request(request, payload, transacao)

        def _validate_signature(
            raw_body: bytes,
            provided_signature: str | None,
            organizacao: Organizacao | None,
        ) -> bool:
            organization_secret = (
                getattr(organizacao, self.organizacao_secret_attr, None) if organizacao else None
            )
            secret = resolve_signature_secret(
                organization_secret,
                self.signature_env_var,
            )
            return validate_hmac_signature(
                raw_body=raw_body,
                provided_signature=provided_signature,
                secret=secret,
            )

        def _confirm_known_transaction(organizacao: Organizacao | None, transacao: Transacao) -> None:
            confirm_known_transaction(
                provider_class=self.provider_class,
                organizacao=organizacao,
                transacao=transacao,
                confirmar_pagamento_com_retry=self._confirmar_pagamento_com_retry,
            )

        def _update_known_transaction(transacao: Transacao) -> None:
            logger.info(
                "webhook_pagamento_confirmado",
                extra={"transacao_id": transacao.id, "external_id": transacao.external_id},
            )
            atualizar_inscricao_transacao_aprovada(transacao=transacao, logger=logger)

        result = execute_payment_webhook_orchestration(
            raw_body=request.body,
            provided_signature=request.headers.get(self.signature_header_name),
            parse_payload=self._parse_body,
            extract_external_id=extract_external_id,
            find_transaction_by_external_id=find_transaction_by_external_id,
            resolve_organizacao=_resolve_organizacao,
            is_signature_valid=_validate_signature,
            confirm_known_transaction=_confirm_known_transaction,
            update_known_transaction=_update_known_transaction,
        )
        if result.reason == "missing_external_id":
            logger.warning("webhook_sem_id")
            return build_webhook_missing_external_id_response()
        if result.reason == "invalid_signature":
            logger.warning("webhook_assinatura_invalida")
            return build_webhook_invalid_signature_response()
        if result.reason == "unknown_transaction":
            logger.info("webhook_transacao_desconhecida", extra={"external_id": result.external_id})
        return build_webhook_processed_response(http_status=result.http_status)

    def _parse_body(self, raw_body: bytes) -> dict[str, Any]:
        return parse_webhook_payload(raw_body)

    def _assinatura_valida(
        self, request: HttpRequest, organizacao: Organizacao | None
    ) -> bool:
        secret = resolve_signature_secret(
            organizacao.mercado_pago_webhook_secret if organizacao else None,
            "MERCADO_PAGO_WEBHOOK_SECRET",
        )
        return validate_hmac_signature(
            raw_body=request.body,
            provided_signature=request.headers.get("X-Signature"),
            secret=secret,
        )

    def _organizacao_from_request(
        self, request: HttpRequest, payload: dict[str, Any], transacao: Transacao | None
    ) -> Organizacao | None:
        return obter_organizacao_webhook(request=request, _payload=payload, transacao=transacao)


class PayPalWebhookView(WebhookView):
    provider_class = PayPalProvider
    signature_header_name = "X-Paypal-Signature"
    signature_env_var = "PAYPAL_WEBHOOK_SECRET"
    organizacao_secret_attr = "paypal_webhook_secret"

    def _assinatura_valida(self, request: HttpRequest, organizacao: Organizacao | None) -> bool:
        secret = resolve_signature_secret(
            organizacao.paypal_webhook_secret if organizacao else None,
            "PAYPAL_WEBHOOK_SECRET",
        )
        return validate_hmac_signature(
            raw_body=request.body,
            provided_signature=request.headers.get("X-Paypal-Signature"),
            secret=secret,
        )


class TransacaoRevisaoView(APIView):
    permission_classes = [IsAdminUser]
    template_name = "pagamentos/transacoes_revisao.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        review_filter = resolve_review_filter(raw_status=request.GET.get("status"))
        transacoes = _transacao_reporting_lookup.list_for_review(statuses=review_filter.statuses)
        contexto = build_transacao_revisao_context(
            transacoes=transacoes,
            status_filtro=review_filter.status_filter,
        )
        return render(request, self.template_name, contexto)


class TransacaoCSVExportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request: HttpRequest) -> HttpResponse:
        transacoes = _transacao_reporting_lookup.list_for_csv()
        conteudo = build_transacoes_csv_content(transacoes=transacoes)
        return build_transacoes_csv_response(conteudo=conteudo)

from __future__ import annotations

import pyotp
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from tokens.models import TOTPDevice
from tokens.utils import get_client_ip

from apps.backend.app.modules.accounts.application.profile_management import (
    ToggleUserStatusCommand,
    ToggleUserStatusUseCase,
)
from apps.backend.app.modules.accounts.application.account_recovery import (
    AccountRecoveryUseCase,
)
from apps.backend.app.modules.accounts.application.account_deletion import (
    AccountDeletionUseCase,
)
from apps.backend.app.modules.accounts.application.account_delete_cancellation import (
    AccountDeleteCancellationUseCase,
)
from apps.backend.app.modules.accounts.application.user_rating import (
    UserRatingStatsUseCase,
)
from apps.backend.app.modules.accounts.application.profile_permissions import (
    can_manage_profile as _can_manage_profile_uc,
)
from apps.backend.app.modules.accounts.infrastructure.account_recovery import (
    CeleryAccountRecoveryNotifier,
    DjangoAccountRecoveryRepository,
    now_provider,
)
from apps.backend.app.modules.accounts.infrastructure.account_delete_cancellation import (
    DjangoAccountDeleteCancellationRepository,
)
from apps.backend.app.modules.accounts.infrastructure.account_audit import (
    DjangoAccountAuditLogger,
)
from apps.backend.app.modules.accounts.infrastructure.account_security_events import (
    DjangoAccountSecurityEventLogger,
)
from apps.backend.app.modules.accounts.infrastructure.account_deletion import (
    DjangoAccountDeletionRepository,
)
from apps.backend.app.modules.accounts.infrastructure.user_rating import (
    DjangoUserRatingStatsRepository,
)
from apps.backend.app.modules.accounts.infrastructure.profile_management import (
    DjangoUserStatusAuditLogger,
    DjangoUserStatusRepository,
)
from apps.backend.app.modules.accounts.interfaces.account_recovery import (
    map_confirm_email_to_api,
    map_request_password_reset_to_api,
    map_resend_result_to_api,
    map_reset_password_to_api,
)
from apps.backend.app.modules.accounts.interfaces.profile_management import (
    map_domain_error_to_api_response,
)
from apps.backend.app.modules.accounts.interfaces.account_delete_cancellation import (
    build_cancel_delete_success_response,
    map_cancel_delete_result_to_api_response,
)
from apps.backend.app.modules.accounts.interfaces.account_deletion import (
    map_delete_me_invalid_confirmation_response,
)
from apps.backend.app.modules.accounts.interfaces.account_two_factor import (
    build_2fa_setup_secret_response,
    map_2fa_already_enabled_response,
    map_2fa_code_required_response,
    map_2fa_disabled_response,
    map_2fa_enabled_response,
    map_2fa_invalid_code_response,
    map_2fa_password_invalid_response,
)
from apps.backend.app.modules.accounts.interfaces.user_rating import (
    build_user_rating_api_response_payload,
)
from apps.backend.app.modules.accounts.interfaces.account_api_responses import (
    build_created_response,
    build_no_content_response,
    build_user_status_response,
)

from .serializers import UserRatingSerializer, UserSerializer
from .tasks import (
    send_cancel_delete_email,
)

User = get_user_model()

_toggle_user_status_uc = ToggleUserStatusUseCase(
    repository=DjangoUserStatusRepository(),
    audit_logger=DjangoUserStatusAuditLogger(),
    can_manage_profile=_can_manage_profile_uc,
)
_account_recovery_uc = AccountRecoveryUseCase(
    repository=DjangoAccountRecoveryRepository(),
    notifier=CeleryAccountRecoveryNotifier(),
    now=now_provider,
)
_account_deletion_uc = AccountDeletionUseCase(
    repository=DjangoAccountDeletionRepository(),
    now=now_provider,
)
_account_delete_cancellation_uc = AccountDeleteCancellationUseCase(
    repository=DjangoAccountDeleteCancellationRepository(),
    now=now_provider,
)
_account_audit_logger = DjangoAccountAuditLogger()
_account_security_event_logger = DjangoAccountSecurityEventLogger()
_user_rating_stats_uc = UserRatingStatsUseCase(
    repository=DjangoUserRatingStatsRepository(),
)


class AccountViewSet(viewsets.GenericViewSet):
    queryset = User.objects.select_related("organizacao", "nucleo")
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in {"delete_me", "enable_2fa", "disable_2fa", "rate_user"}:
            return [IsAuthenticated()]
        return [AllowAny()]

    @action(detail=False, methods=["post"], url_path="confirm-email")
    def confirm_email(self, request):
        result = _account_recovery_uc.confirm_email_token(
            code=request.data.get("token"),
            ip=get_client_ip(request),
        )
        return map_confirm_email_to_api(result.status)

    @action(detail=False, methods=["post"], url_path="resend-confirmation")
    @method_decorator(ratelimit(key="ip", rate="5/h", method="POST", block=True))
    def resend_confirmation(self, request):
        result = _account_recovery_uc.resend_confirmation(
            email=request.data.get("email"),
            ip=get_client_ip(request),
        )
        return map_resend_result_to_api(result.status)

    @action(detail=False, methods=["post"], url_path="request-password-reset")
    @method_decorator(ratelimit(key="ip", rate="5/h", method="POST", block=True))
    def request_password_reset(self, request):
        result = _account_recovery_uc.request_password_reset(
            email=request.data.get("email"),
            ip=get_client_ip(request),
        )
        return map_request_password_reset_to_api(result.status)

    @action(detail=False, methods=["post"], url_path="reset-password")
    def reset_password(self, request):
        result = _account_recovery_uc.reset_password(
            code=request.data.get("token"),
            raw_password=request.data.get("password"),
            ip=get_client_ip(request),
        )
        return map_reset_password_to_api(result.status, result.errors)

    @action(detail=True, methods=["post"], url_path="rate", permission_classes=[IsAuthenticated])
    def rate_user(self, request, pk=None):
        target_user = self.get_object()
        serializer = UserRatingSerializer(
            data=request.data,
            context={"request": request, "rated_user": target_user},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        stats = _user_rating_stats_uc.execute(rated_user=target_user)
        response_data = build_user_rating_api_response_payload(
            serializer_data=serializer.data,
            rating_stats=stats,
        )
        return build_created_response(payload=response_data)

    @action(detail=False, methods=["post"], url_path="enable-2fa")
    def enable_2fa(self, request):
        user = request.user
        ip = get_client_ip(request)
        password = request.data.get("password")
        if not password or not user.check_password(password):
            _account_security_event_logger.log_2fa_enable_failed(user=user, ip=ip)
            return map_2fa_password_invalid_response()
        code = request.data.get("code")
        if user.two_factor_enabled:
            return map_2fa_already_enabled_response()
        if not user.two_factor_secret:
            secret = pyotp.random_base32()
            user.two_factor_secret = secret
            user.save(update_fields=["two_factor_secret"])
            otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=user.email, issuer_name="Hubx")
            return build_2fa_setup_secret_response(otp_uri=otp_uri, secret=secret)
        if not code:
            return map_2fa_code_required_response()
        if not pyotp.TOTP(user.two_factor_secret).verify(code):
            return map_2fa_invalid_code_response()
        user.two_factor_enabled = True
        user.save(update_fields=["two_factor_enabled"])
        TOTPDevice.all_objects.update_or_create(
            usuario=user,
            defaults={
                "secret": user.two_factor_secret,
                "confirmado": True,
                "deleted": False,
                "deleted_at": None,
            },
        )
        _account_security_event_logger.log_2fa_enabled(user=user, ip=ip)
        return map_2fa_enabled_response()

    @action(detail=False, methods=["post"], url_path="disable-2fa")
    def disable_2fa(self, request):
        user = request.user
        ip = get_client_ip(request)
        password = request.data.get("password")
        code = request.data.get("code")
        if not password or not user.check_password(password):
            _account_security_event_logger.log_2fa_disable_failed(user=user, ip=ip)
            return map_2fa_password_invalid_response()
        if not code:
            return map_2fa_code_required_response()
        if not user.two_factor_secret or not pyotp.TOTP(user.two_factor_secret).verify(code):
            return map_2fa_invalid_code_response()
        user.two_factor_enabled = False
        user.two_factor_secret = None
        user.save(update_fields=["two_factor_enabled", "two_factor_secret"])
        TOTPDevice.objects.filter(usuario=user).delete()
        _account_security_event_logger.log_2fa_disabled(user=user, ip=ip)
        return map_2fa_disabled_response()

    @action(detail=False, methods=["delete"], url_path="me")
    def delete_me(self, request):
        user = request.user
        password = request.data.get("password")
        confirm = request.data.get("confirm")
        valid = False
        if password:
            valid = user.check_password(password)
        elif confirm:
            valid = confirm == "EXCLUIR"
        if not valid:
            _account_security_event_logger.log_account_delete_failed(
                user=user,
                ip=get_client_ip(request),
            )
            return map_delete_me_invalid_confirmation_response()
        deletion_result = _account_deletion_uc.execute(
            user=user,
            ip=get_client_ip(request),
        )
        if deletion_result.token_id:
            send_cancel_delete_email.delay(deletion_result.token_id)
        return build_no_content_response()

    @action(detail=False, methods=["post"], url_path="me/cancel-delete")
    def cancel_delete(self, request):
        result = _account_delete_cancellation_uc.execute(
            code=request.data.get("token"),
            ip=get_client_ip(request),
        )
        ip = get_client_ip(request)
        error_response = map_cancel_delete_result_to_api_response(result_status=result.status)
        if error_response is not None:
            return error_response
        return build_cancel_delete_success_response(
            user=result.user,
            ip=ip,
            audit_logger=_account_audit_logger,
        )

    @action(detail=True, methods=["post"], url_path="deactivate", permission_classes=[IsAuthenticated])
    def deactivate(self, request, pk=None):
        target_user = self.get_object()
        try:
            _toggle_user_status_uc.deactivate(
                ToggleUserStatusCommand(
                    actor=request.user,
                    target=target_user,
                    ip=get_client_ip(request),
                )
            )
        except Exception as exc:
            return map_domain_error_to_api_response(exc)
        return build_user_status_response(
            user=target_user,
            activated=False,
        )

    @action(detail=True, methods=["post"], url_path="activate", permission_classes=[IsAuthenticated])
    def activate(self, request, pk=None):
        target_user = self.get_object()
        try:
            _toggle_user_status_uc.activate(
                ToggleUserStatusCommand(
                    actor=request.user,
                    target=target_user,
                    ip=get_client_ip(request),
                )
            )
        except Exception as exc:
            return map_domain_error_to_api_response(exc)
        return build_user_status_response(
            user=target_user,
            activated=True,
        )

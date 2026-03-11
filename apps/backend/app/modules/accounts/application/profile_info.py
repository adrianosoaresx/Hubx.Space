from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ProfileInfoForm(Protocol):
    email_changed: bool

    def is_valid(self) -> bool: ...

    def save(self): ...


class ProfileInfoFormGateway(Protocol):
    def create_bound(self, *, data, files, instance) -> ProfileInfoForm: ...

    def create_unbound(self, *, instance) -> ProfileInfoForm: ...


@dataclass(frozen=True)
class ProfileInfoSubmitResult:
    success: bool
    form: ProfileInfoForm
    email_changed: bool = False


class ProfileInfoUseCase:
    def __init__(self, *, form_gateway: ProfileInfoFormGateway) -> None:
        self._form_gateway = form_gateway

    @staticmethod
    def should_redirect_to_edit(*, method: str, is_htmx: bool) -> bool:
        return method in {"GET", "HEAD"} and not is_htmx

    @staticmethod
    def build_target_identifiers(*, target_user, is_self: bool) -> dict[str, str]:
        if is_self:
            return {}
        return {
            "public_id": str(target_user.public_id),
            "username": target_user.username,
        }

    @staticmethod
    def build_edit_params(target_identifiers: dict[str, str]) -> dict[str, str | None]:
        params: dict[str, str | None] = {"info_view": "edit"}
        params.update(target_identifiers)
        return params

    @staticmethod
    def build_view_params(target_identifiers: dict[str, str]) -> dict[str, str | None]:
        params: dict[str, str | None] = {"info_view": None}
        params.update(target_identifiers)
        return params

    @staticmethod
    def build_success_feedback(*, email_changed: bool, is_self: bool, target_display_name: str) -> tuple[str, str]:
        if email_changed:
            if is_self:
                return "info", "Confirme o novo e-mail enviado."
            return "info", "O usuário deverá confirmar o novo e-mail enviado."

        if is_self:
            return "success", "Informações do perfil atualizadas."
        return "success", f"Informações do perfil de {target_display_name} atualizadas."

    def submit(self, *, data, files, target_user) -> ProfileInfoSubmitResult:
        form = self._form_gateway.create_bound(data=data, files=files, instance=target_user)
        if not form.is_valid():
            return ProfileInfoSubmitResult(success=False, form=form, email_changed=False)

        form.save()
        return ProfileInfoSubmitResult(
            success=True,
            form=form,
            email_changed=bool(getattr(form, "email_changed", False)),
        )

    def new_form(self, *, target_user) -> ProfileInfoForm:
        return self._form_gateway.create_unbound(instance=target_user)

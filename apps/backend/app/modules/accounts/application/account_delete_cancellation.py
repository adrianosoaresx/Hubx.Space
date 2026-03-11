from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class AccountDeleteCancellationRepository(Protocol):
    def find_cancel_delete_token(self, *, code: str): ...

    def reactivate_user_from_cancel_token(self, *, token, ip: str | None): ...


@dataclass(frozen=True)
class AccountDeleteCancellationResult:
    status: str
    user: object | None = None


class AccountDeleteCancellationUseCase:
    def __init__(
        self,
        *,
        repository: AccountDeleteCancellationRepository,
        now,
    ) -> None:
        self._repository = repository
        self._now = now

    def execute(self, *, code: str | None, ip: str | None) -> AccountDeleteCancellationResult:
        if not code:
            return AccountDeleteCancellationResult(status="missing_token")

        token = self._repository.find_cancel_delete_token(code=code)
        if token is None:
            return AccountDeleteCancellationResult(status="invalid_or_expired")
        if token.expires_at < self._now() or token.used_at:
            return AccountDeleteCancellationResult(status="invalid_or_expired")

        user = self._repository.reactivate_user_from_cancel_token(
            token=token,
            ip=ip,
        )
        return AccountDeleteCancellationResult(status="success", user=user)

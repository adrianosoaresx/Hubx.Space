from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Protocol


class AccountDeletionRepository(Protocol):
    def delete_account_and_issue_cancel_token(
        self,
        *,
        user,
        ip: str | None,
        expires_at,
    ): ...


@dataclass(frozen=True)
class AccountDeletionResult:
    token_id: int | None


class AccountDeletionUseCase:
    def __init__(
        self,
        *,
        repository: AccountDeletionRepository,
        now,
    ) -> None:
        self._repository = repository
        self._now = now

    def execute(self, *, user, ip: str | None) -> AccountDeletionResult:
        token = self._repository.delete_account_and_issue_cancel_token(
            user=user,
            ip=ip,
            expires_at=self._now() + timedelta(days=30),
        )
        return AccountDeletionResult(token_id=getattr(token, "id", None))

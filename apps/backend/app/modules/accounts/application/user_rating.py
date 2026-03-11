from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class UserRatingStats:
    average: float | None
    total: int
    display: str


class UserRatingStatsRepository(Protocol):
    def aggregate_for_user(self, *, rated_user) -> UserRatingStats: ...


class UserRatingStatsUseCase:
    def __init__(self, *, repository: UserRatingStatsRepository) -> None:
        self._repository = repository

    def execute(self, *, rated_user) -> UserRatingStats:
        return self._repository.aggregate_for_user(rated_user=rated_user)

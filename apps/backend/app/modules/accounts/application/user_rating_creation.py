from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CreateUserRatingCommand:
    rated_by: object
    rated_user: object
    score: int
    comment: str


class UserRatingCreationRepository(Protocol):
    def create_user_rating(self, *, command: CreateUserRatingCommand): ...


class UserRatingCreationUseCase:
    def __init__(self, *, repository: UserRatingCreationRepository) -> None:
        self._repository = repository

    def execute(self, *, command: CreateUserRatingCommand):
        return self._repository.create_user_rating(command=command)

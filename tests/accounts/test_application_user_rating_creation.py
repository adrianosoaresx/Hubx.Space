import os
from types import SimpleNamespace

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.accounts.application.user_rating_creation import (  # noqa: E402
    CreateUserRatingCommand,
    UserRatingCreationUseCase,
)


class _FakeRepository:
    def __init__(self, created):
        self.created = created
        self.calls = []

    def create_user_rating(self, *, command):
        self.calls.append(command)
        return self.created


def test_user_rating_creation_use_case_delegates_to_repository():
    created = SimpleNamespace(id=99)
    fake_repository = _FakeRepository(created=created)
    use_case = UserRatingCreationUseCase(repository=fake_repository)

    command = CreateUserRatingCommand(
        rated_by=SimpleNamespace(id=1),
        rated_user=SimpleNamespace(id=2),
        score=4,
        comment="Bom",
    )
    result = use_case.execute(command=command)

    assert result == created
    assert fake_repository.calls == [command]

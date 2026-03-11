import os
from types import SimpleNamespace

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.accounts.application.user_rating import (  # noqa: E402
    UserRatingStats,
    UserRatingStatsUseCase,
)


class _FakeRepository:
    def __init__(self, stats):
        self.stats = stats
        self.calls = []

    def aggregate_for_user(self, *, rated_user):
        self.calls.append(rated_user)
        return self.stats


def test_user_rating_stats_use_case_returns_repository_stats():
    expected = UserRatingStats(average=4.5, total=8, display="4,5")
    fake_repository = _FakeRepository(stats=expected)
    use_case = UserRatingStatsUseCase(repository=fake_repository)
    user = SimpleNamespace(id=10)

    result = use_case.execute(rated_user=user)

    assert result == expected
    assert fake_repository.calls == [user]

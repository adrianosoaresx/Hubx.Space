from __future__ import annotations

from django.db.models import Avg, Count

from accounts.models import UserRating

from apps.backend.app.modules.accounts.application.user_rating import UserRatingStats


class DjangoUserRatingStatsRepository:
    def aggregate_for_user(self, *, rated_user) -> UserRatingStats:
        stats = UserRating.objects.filter(rated_user=rated_user).aggregate(
            media=Avg("score"),
            total=Count("id"),
        )
        average = stats["media"]
        display = f"{average:.1f}".replace(".", ",") if average is not None else ""
        return UserRatingStats(
            average=average,
            total=stats["total"],
            display=display,
        )

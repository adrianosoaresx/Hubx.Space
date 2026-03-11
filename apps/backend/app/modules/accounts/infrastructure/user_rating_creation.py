from __future__ import annotations

from accounts.models import UserRating


class DjangoUserRatingCreationRepository:
    def create_user_rating(self, *, command):
        rating = UserRating(
            rated_by=command.rated_by,
            rated_user=command.rated_user,
            score=command.score,
            comment=command.comment,
        )
        rating.full_clean_with_user(command.rated_by)
        rating.save()
        return rating

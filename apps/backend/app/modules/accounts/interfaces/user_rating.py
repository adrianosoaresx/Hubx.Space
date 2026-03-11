from __future__ import annotations


def build_user_rating_api_response_payload(*, serializer_data: dict, rating_stats) -> dict:
    return serializer_data | {
        "average": rating_stats.average,
        "display": rating_stats.display,
        "total": rating_stats.total,
    }

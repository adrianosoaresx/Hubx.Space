from __future__ import annotations

from typing import Any


def resolve_portfolio_query(filter_form) -> str:
    if filter_form.is_valid():
        return filter_form.cleaned_data.get("q", "") or ""
    return ""


def resolve_portfolio_show_form(
    *,
    can_manage_portfolio: bool,
    query_add_flag: bool,
    force_show_flag: bool,
) -> bool:
    if not can_manage_portfolio:
        return False
    return query_add_flag or force_show_flag


def resolve_portfolio_selection_state(
    *,
    all_portfolio_medias: list[Any],
    portfolio_media_id: str | None,
    portfolio_show_form: bool,
) -> dict[str, Any]:
    portfolio_selected_media = None
    portfolio_show_detail = False
    portfolio_force_open = portfolio_show_form
    updated_show_form = portfolio_show_form

    if portfolio_media_id:
        portfolio_selected_media = next(
            (media for media in all_portfolio_medias if str(media.pk) == str(portfolio_media_id)),
            None,
        )
        if portfolio_selected_media is not None:
            portfolio_show_detail = True
            updated_show_form = False
            portfolio_force_open = True

    return {
        "portfolio_selected_media": portfolio_selected_media,
        "portfolio_show_detail": portfolio_show_detail,
        "portfolio_force_open": portfolio_force_open,
        "portfolio_show_form": updated_show_form,
    }


def resolve_portfolio_navigation_state(*, query_params, request_path: str) -> dict[str, str]:
    params_without_detail = query_params.copy()
    params_without_detail.pop("portfolio_midia", None)
    params_without_detail.pop("portfolio_adicionar", None)
    portfolio_query_base = params_without_detail.urlencode()
    portfolio_detail_back_url = request_path
    if portfolio_query_base:
        portfolio_detail_back_url = f"{request_path}?{portfolio_query_base}"
    return {
        "portfolio_query_base": portfolio_query_base,
        "portfolio_detail_back_url": portfolio_detail_back_url,
    }

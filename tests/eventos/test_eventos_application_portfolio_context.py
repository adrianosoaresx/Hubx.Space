import os
from types import SimpleNamespace

import django
from django.http import QueryDict

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hubx.settings")
django.setup()

from apps.backend.app.modules.eventos.application.portfolio_context import (
    resolve_portfolio_navigation_state,
    resolve_portfolio_query,
    resolve_portfolio_selection_state,
    resolve_portfolio_show_form,
)


class _FormValid:
    cleaned_data = {"q": "banner"}

    @staticmethod
    def is_valid():
        return True


class _FormInvalid:
    cleaned_data = {}

    @staticmethod
    def is_valid():
        return False


def test_resolve_portfolio_query_valid_form():
    assert resolve_portfolio_query(_FormValid()) == "banner"


def test_resolve_portfolio_query_invalid_form():
    assert resolve_portfolio_query(_FormInvalid()) == ""


def test_resolve_portfolio_show_form():
    assert resolve_portfolio_show_form(
        can_manage_portfolio=True,
        query_add_flag=True,
        force_show_flag=False,
    ) is True
    assert resolve_portfolio_show_form(
        can_manage_portfolio=False,
        query_add_flag=True,
        force_show_flag=True,
    ) is False


def test_resolve_portfolio_selection_state_selects_media():
    medias = [SimpleNamespace(pk=1), SimpleNamespace(pk=2)]
    state = resolve_portfolio_selection_state(
        all_portfolio_medias=medias,
        portfolio_media_id="2",
        portfolio_show_form=True,
    )
    assert state["portfolio_selected_media"].pk == 2
    assert state["portfolio_show_detail"] is True
    assert state["portfolio_show_form"] is False
    assert state["portfolio_force_open"] is True


def test_resolve_portfolio_navigation_state():
    query = QueryDict("portfolio_midia=2&portfolio_adicionar=1&q=abc")
    state = resolve_portfolio_navigation_state(query_params=query, request_path="/eventos/evento/1/")
    assert state["portfolio_query_base"] == "q=abc"
    assert state["portfolio_detail_back_url"] == "/eventos/evento/1/?q=abc"

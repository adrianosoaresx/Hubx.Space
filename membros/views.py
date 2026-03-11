from __future__ import annotations

from urllib.parse import urlparse

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Exists, OuterRef, Q
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, ListView, TemplateView, View
from django.template.loader import render_to_string

from accounts.models import UserType
from apps.backend.app.modules.membros.application.membership_policies import (
    can_access_promocao,
    resolve_allowed_user_types_for_creator,
)
from apps.backend.app.modules.membros.application.promotion_form_context import (
    build_promocao_form_context,
)
from apps.backend.app.modules.membros.application.promotion_workflow import (
    execute_promocao_from_post,
)
from core.permissions import MembrosRequiredMixin, NoSuperadminMixin
from core.utils import resolve_back_href
from nucleos.models import Nucleo, ParticipacaoNucleo

from .forms import OrganizacaoUserCreateForm

User = get_user_model()

MEMBRO_PROMOVER_CAROUSEL_PAGE_SIZE = 6


class MembrosPermissionMixin(MembrosRequiredMixin, NoSuperadminMixin):
    """Combines permission checks for membros views."""

    raise_exception = True

    def test_func(self):
        return MembrosRequiredMixin.test_func(self) and NoSuperadminMixin.test_func(self)


class MembrosPromocaoPermissionMixin(MembrosPermissionMixin):
    """Restricts acesso às telas de promoção a admins e operadores."""

    def test_func(self):
        if not super().test_func():
            return False
        tipo_usuario = getattr(self.request.user, "get_tipo_usuario", None)
        return can_access_promocao(tipo_usuario)


class OrganizacaoUserCreateView(NoSuperadminMixin, LoginRequiredMixin, FormView):
    template_name = "membros/usuario_form.html"
    form_class = OrganizacaoUserCreateForm
    success_url = reverse_lazy("membros:membros_lista")

    def dispatch(self, request, *args, **kwargs):
        allowed_types = self.get_allowed_user_types()
        if not allowed_types or getattr(request.user, "organizacao_id", None) is None:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_allowed_user_types(self) -> list[str]:
        tipo_usuario = getattr(self.request.user, "get_tipo_usuario", None)
        return resolve_allowed_user_types_for_creator(tipo_usuario)

    def get_initial(self):
        initial = super().get_initial()
        requested_type = self.request.GET.get("tipo")
        if requested_type in self.get_allowed_user_types():
            initial["user_type"] = requested_type
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["allowed_user_types"] = self.get_allowed_user_types()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fallback_url = reverse("membros:membros_lista")
        back_href = resolve_back_href(self.request, fallback=fallback_url)
        context["back_href"] = back_href
        context["back_component_config"] = {
            "href": back_href,
            "fallback_href": fallback_url,
        }
        context["cancel_component_config"] = {
            "href": fallback_url,
            "fallback_href": fallback_url,
            "prevent_history": True,
        }
        return context

    def form_valid(self, form):
        organizacao = getattr(self.request.user, "organizacao", None)
        if organizacao is None:
            raise PermissionDenied

        try:
            new_user = form.save(organizacao=organizacao)
        except IntegrityError as exc:
            error_message = str(exc)
            if "accounts_user.cnpj" in error_message:
                form.add_error("cnpj", _("Este CNPJ informado já está em uso."))
            elif "accounts_user_unique_cpf_without_cnpj" in error_message:
                form.add_error(None, _("Cnpj ou Cpf já cadastrado."))
            else:
                form.add_error(None, _("Não foi possível salvar o usuário. Tente novamente."))
            return self.form_invalid(form)

        type_labels = {value: label for value, label in UserType.choices}
        tipo_display = type_labels.get(new_user.user_type, new_user.user_type)
        messages.success(
            self.request,
            _("Usuário %(username)s (%(tipo)s) adicionado com sucesso.")
            % {
                "username": new_user.get_full_name(),
                "tipo": tipo_display,
            },
        )
        return super().form_valid(form)

    def _get_post_redirect_target(self) -> str | None:
        candidate = self.request.POST.get("next")
        if not candidate:
            return None

        if not url_has_allowed_host_and_scheme(
            candidate,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return None

        parsed = urlparse(candidate)
        path = parsed.path or ""
        if parsed.query:
            path = f"{path}?{parsed.query}"
        if parsed.fragment:
            path = f"{path}#{parsed.fragment}"

        return path or candidate

    def get_success_url(self):
        redirect_target = self._get_post_redirect_target()
        if redirect_target and redirect_target != self.request.path:
            return redirect_target
        return super().get_success_url()


class MembroListDataMixin:
    sections = (
        "sem_nucleo",
        "nucleados",
        "consultores",
        "coordenadores",
        "inativos",
        "leads",
    )
    paginate_by = 6

    def get_paginate_by(self) -> int:
        try:
            per_page = int(self.request.GET.get("per_page", self.paginate_by))
        except (TypeError, ValueError):
            return self.paginate_by
        return per_page if per_page > 0 else self.paginate_by

    def get_search_term(self) -> str:
        return (self.request.GET.get("q") or "").strip()

    def get_consultor_filter(self) -> Q:
        return Q(user_type=UserType.CONSULTOR.value)

    def get_coordenador_filter(self) -> Q:
        return (
            Q(user_type=UserType.COORDENADOR.value)
            | Q(is_coordenador=True)
            | Q(
                participacoes__papel="coordenador",
                participacoes__status="ativo",
                participacoes__status_suspensao=False,
            )
        )

    def get_filtered_queryset(self):
        User = get_user_model()
        organizacao = getattr(self.request.user, "organizacao", None)
        queryset = (
            User.objects.filter(organizacao=organizacao)
            .filter(
                Q(is_associado=True)
                | Q(
                    user_type__in=[
                        UserType.NUCLEADO.value,
                        UserType.COORDENADOR.value,
                        UserType.CONSULTOR.value,
                        UserType.CONVIDADO.value,
                    ]
                )
                | Q(is_coordenador=True)
            )
            .select_related("organizacao", "nucleo")
            .prefetch_related("participacoes__nucleo", "nucleos_consultoria")
            .annotate(_order=Lower("username"))
            .order_by("_order", "id")
        )

        search_term = self.get_search_term()
        if search_term:
            queryset = queryset.filter(
                Q(username__icontains=search_term) | Q(contato__icontains=search_term)
            )

        return queryset.distinct()

    def get_section_queryset(self, base_queryset, section: str):
        active_participacao = ParticipacaoNucleo.objects.filter(
            user=OuterRef("pk"),
            status="ativo",
            status_suspensao=False,
        )
        if section == "sem_nucleo":
            excluded_user_types = {UserType.ADMIN.value, UserType.OPERADOR.value}
            return (
                base_queryset.filter(is_associado=True, is_active=True)
                .exclude(user_type__in=excluded_user_types)
                .annotate(has_active_participacao=Exists(active_participacao))
                .filter(has_active_participacao=False)
            )
        if section == "nucleados":
            return (
                base_queryset.filter(is_associado=True, is_active=True)
                .annotate(has_active_participacao=Exists(active_participacao))
                .filter(has_active_participacao=True)
            )
        if section == "consultores":
            return base_queryset.filter(self.get_consultor_filter(), is_active=True)
        if section == "coordenadores":
            return base_queryset.filter(self.get_coordenador_filter(), is_active=True)
        if section == "inativos":
            return base_queryset.filter(is_active=False)
        if section == "leads":
            return base_queryset.filter(user_type=UserType.CONVIDADO.value)
        raise ValueError(f"Unknown section '{section}'")

    def get_section_page(self, base_queryset, section: str, *, page_number=None):
        queryset = self.get_section_queryset(base_queryset, section)
        paginator = Paginator(queryset, self.get_paginate_by())
        number = page_number or self.request.GET.get(f"{section}_page") or 1
        page_obj = paginator.get_page(number)
        return page_obj, paginator

    def get_empty_message(self, section: str) -> str:
        messages = {
            "sem_nucleo": _("Nenhum membro sem núcleo encontrado."),
            "nucleados": _("Nenhum membro nucleado encontrado."),
            "consultores": _("Nenhum consultor encontrado."),
            "coordenadores": _("Nenhum coordenador encontrado."),
            "inativos": _("Nenhum usuário inativo encontrado."),
            "leads": _("Nenhum lead encontrado."),
        }
        return messages.get(section, _("Nenhum usuário encontrado."))

    def get_totals(self) -> dict[str, int]:
        User = get_user_model()
        organizacao = getattr(self.request.user, "organizacao", None)
        if organizacao is None:
            return {
                "total_usuarios": 0,
                "total_membros": 0,
                "total_nucleados": 0,
                "total_consultores": 0,
                "total_coordenadores": 0,
                "total_inativos": 0,
                "total_leads": 0,
            }

        base_queryset = User.objects.filter(organizacao=organizacao)
        active_participacao = ParticipacaoNucleo.objects.filter(
            user=OuterRef("pk"),
            status="ativo",
            status_suspensao=False,
        )

        excluded_user_types = {UserType.ADMIN.value, UserType.OPERADOR.value}

        total_membros = (
            base_queryset.filter(is_associado=True, is_active=True)
            .exclude(user_type__in=excluded_user_types)
            .annotate(has_active_participacao=Exists(active_participacao))
            .filter(has_active_participacao=False)
            .count()
        )
        total_nucleados = (
            base_queryset.filter(is_associado=True, is_active=True)
            .annotate(has_active_participacao=Exists(active_participacao))
            .filter(has_active_participacao=True)
            .count()
        )

        total_inativos = (
            base_queryset.filter(
                Q(is_associado=True)
                | Q(
                    user_type__in=[
                        UserType.NUCLEADO.value,
                        UserType.COORDENADOR.value,
                        UserType.CONSULTOR.value,
                    ]
                )
                | Q(is_coordenador=True)
            )
            .filter(is_active=False)
            .distinct()
            .count()
        )

        return {
            "total_usuarios": base_queryset.count(),
            "total_membros": total_membros,
            "total_nucleados": total_nucleados,
            "total_consultores": User.objects.filter(organizacao=organizacao)
            .filter(self.get_consultor_filter(), is_active=True)
            .distinct()
            .count(),
            "total_coordenadores": User.objects.filter(organizacao=organizacao)
            .filter(self.get_coordenador_filter(), is_active=True)
            .distinct()
            .count(),
            "total_inativos": total_inativos,
            "total_leads": base_queryset.filter(user_type=UserType.CONVIDADO.value).count(),
        }


class MembroListView(
    MembrosPermissionMixin,
    LoginRequiredMixin,
    MembroListDataMixin,
    TemplateView,
):
    template_name = "membros/membro_list.html"

    def get_open_section(self) -> str:
        section = (self.request.GET.get("section") or "").strip()
        if section in self.sections:
            return section
        return ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_queryset = self.get_filtered_queryset()

        section_pages: dict[str, dict[str, object]] = {}
        for section in self.sections:
            page_obj, paginator = self.get_section_page(base_queryset, section)
            section_pages[section] = {
                "page": page_obj,
                "count": paginator.count,
                "total_pages": paginator.num_pages,
            }

        context.update(
            {
                "search_term": self.get_search_term(),
                "membros_fetch_url": reverse("membros:membros_lista_api"),
                "membros_sem_nucleo_page": section_pages["sem_nucleo"]["page"],
                "membros_sem_nucleo_count": section_pages["sem_nucleo"]["count"],
                "membros_nucleados_page": section_pages["nucleados"]["page"],
                "membros_nucleados_count": section_pages["nucleados"]["count"],
                "membros_consultores_page": section_pages["consultores"]["page"],
                "membros_consultores_count": section_pages["consultores"]["count"],
                "membros_coordenadores_page": section_pages["coordenadores"]["page"],
                "membros_coordenadores_count": section_pages["coordenadores"]["count"],
                "membros_inativos_page": section_pages["inativos"]["page"],
                "membros_inativos_count": section_pages["inativos"]["count"],
                "membros_leads_page": section_pages["leads"]["page"],
                "membros_leads_count": section_pages["leads"]["count"],
                "membros_section_empty_messages": {
                    section: self.get_empty_message(section)
                    for section in self.sections
                },
                "open_section": self.get_open_section(),
            }
        )

        context.update(self.get_totals())
        return context


class MembroSectionListView(
    MembrosPermissionMixin,
    LoginRequiredMixin,
    MembroListDataMixin,
    View,
):
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        section = request.GET.get("section")
        if section not in self.sections:
            return JsonResponse({"error": _("Seção inválida.")}, status=400)

        show_promote_button = (
            (request.GET.get("show_promote_button") or "").lower() in {"1", "true", "on", "yes"}
        )

        base_queryset = self.get_filtered_queryset()
        page_obj, paginator = self.get_section_page(
            base_queryset, section, page_number=request.GET.get("page")
        )

        slide_template = "membros/partials/carousel_slide.html"
        if show_promote_button:
            slide_template = "membros/partials/promover_carousel_slide.html"

        html = render_to_string(
            slide_template,
            {
                "usuarios": page_obj.object_list,
                "page_number": page_obj.number,
                "empty_message": self.get_empty_message(section),
                "section": section,
                "show_promote_button": show_promote_button,
            },
            request=request,
        )

        return JsonResponse(
            {
                "html": html,
                "page": page_obj.number,
                "total_pages": paginator.num_pages,
                "count": paginator.count,
            }
        )


class MembroPromoverListView(MembrosPromocaoPermissionMixin, LoginRequiredMixin, ListView):
    template_name = "membros/promover_list.html"
    context_object_name = "membros"
    paginate_by = MEMBRO_PROMOVER_CAROUSEL_PAGE_SIZE

    def get_queryset(self):
        User = get_user_model()
        organizacao = getattr(self.request.user, "organizacao", None)
        self.organizacao = organizacao
        if organizacao is None:
            self.search_term = ""
            return User.objects.none()

        base_queryset = (
            User.objects.filter(organizacao=organizacao)
            .filter(
                Q(
                    user_type__in=[
                        UserType.COORDENADOR.value,
                        UserType.CONSULTOR.value,
                        UserType.ASSOCIADO.value,
                        UserType.NUCLEADO.value,
                        UserType.CONVIDADO.value,
                    ]
                )
                | Q(is_associado=True)
                | Q(is_coordenador=True)
            )
            .select_related("organizacao", "nucleo")
            .prefetch_related("participacoes__nucleo", "nucleos_consultoria")
        )

        search_term = (self.request.GET.get("q") or "").strip()
        self.search_term = search_term

        if search_term:
            base_queryset = base_queryset.filter(
                Q(username__icontains=search_term)
                | Q(contato__icontains=search_term)
                | Q(nome_fantasia__icontains=search_term)
                | Q(razao_social__icontains=search_term)
                | Q(cnpj__icontains=search_term)
            )

        consultor_filter = Q(user_type=UserType.CONSULTOR.value)
        coordenador_filter = (
            Q(user_type=UserType.COORDENADOR.value)
            | Q(is_coordenador=True)
            | Q(
                participacoes__papel="coordenador",
                participacoes__status="ativo",
                participacoes__status_suspensao=False,
            )
        )

        filtro_tipo = self.request.GET.get("tipo")
        if filtro_tipo == "membros":
            base_queryset = base_queryset.filter(is_associado=True, nucleo__isnull=True)
        elif filtro_tipo == "nucleados":
            base_queryset = base_queryset.filter(is_associado=True, nucleo__isnull=False)
        elif filtro_tipo == "consultores":
            base_queryset = base_queryset.filter(consultor_filter)
        elif filtro_tipo == "coordenadores":
            base_queryset = base_queryset.filter(coordenador_filter)

        base_queryset = base_queryset.distinct()

        base_queryset = base_queryset.annotate(_order_name=Lower("username"))
        return base_queryset.order_by("_order_name", "id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_term"] = getattr(self, "search_term", "")

        current_filter = self.get_current_filter()

        params = self.request.GET.copy()
        if "page" in params:
            params.pop("page")

        valid_filters = {"membros", "nucleados", "consultores", "coordenadores"}

        def build_url(filter_value: str | None) -> str:
            query_params = params.copy()
            if filter_value in valid_filters:
                query_params["tipo"] = filter_value
            else:
                query_params.pop("tipo", None)
            query_string = query_params.urlencode()
            return f"{self.request.path}?{query_string}" if query_string else self.request.path

        context["current_filter"] = current_filter
        context["membros_filter_url"] = build_url("membros")
        context["nucleados_filter_url"] = build_url("nucleados")
        context["consultores_filter_url"] = build_url("consultores")
        context["coordenadores_filter_url"] = build_url("coordenadores")
        context["todos_filter_url"] = build_url(None)
        context["is_membros_filter_active"] = current_filter == "membros"
        context["is_nucleados_filter_active"] = current_filter == "nucleados"
        context["is_consultores_filter_active"] = current_filter == "consultores"
        context["is_coordenadores_filter_active"] = current_filter == "coordenadores"

        organizacao = getattr(self, "organizacao", None)
        User = get_user_model()
        if organizacao:
            context["total_usuarios"] = User.objects.filter(organizacao=organizacao).count()
            context["total_membros"] = User.objects.filter(
                organizacao=organizacao, is_associado=True, nucleo__isnull=True
            ).count()
            context["total_nucleados"] = User.objects.filter(
                organizacao=organizacao, is_associado=True, nucleo__isnull=False
            ).count()
            consultor_filter = Q(user_type=UserType.CONSULTOR.value)
            context["total_consultores"] = (
                User.objects.filter(organizacao=organizacao).filter(consultor_filter).distinct().count()
            )
            coordenador_filter = (
                Q(user_type=UserType.COORDENADOR.value)
                | Q(is_coordenador=True)
                | Q(
                    participacoes__papel="coordenador",
                    participacoes__status="ativo",
                    participacoes__status_suspensao=False,
                )
            )
            context["total_coordenadores"] = (
                User.objects.filter(organizacao=organizacao).filter(coordenador_filter).distinct().count()
            )
        else:
            context["total_usuarios"] = 0
            context["total_membros"] = 0
            context["total_nucleados"] = 0
            context["total_consultores"] = 0
            context["total_coordenadores"] = 0

        context["has_search"] = bool(context["search_term"].strip())
        context["promover_empty_message"] = self.get_empty_message()
        context["promover_carousel_fetch_url"] = reverse(
            "membros:membros_promover_carousel"
        )
        return context

    def get_current_filter(self) -> str:
        valid_filters = {"membros", "nucleados", "consultores", "coordenadores"}
        current_filter = self.request.GET.get("tipo") or ""
        if current_filter not in valid_filters:
            return "todos"
        return current_filter

    def get_empty_message(self) -> str:
        if getattr(self, "search_term", "").strip():
            return _("Nenhum membro encontrado para a busca informada.")
        return _("Nenhum membro disponível para promoção no momento.")


class MembroPromoverCarouselView(MembrosPromocaoPermissionMixin, View):
    def get(self, request, *args, **kwargs):
        list_view = MembroPromoverListView()
        list_view.request = request
        list_view.args = ()
        list_view.kwargs = {}

        queryset = list_view.get_queryset()
        paginator = Paginator(queryset, MEMBRO_PROMOVER_CAROUSEL_PAGE_SIZE)
        page_obj = paginator.get_page(request.GET.get("page") or 1)

        empty_message = list_view.get_empty_message()

        html = render_to_string(
            "membros/partials/promover_carousel_slide.html",
            {
                "usuarios": page_obj.object_list,
                "page_number": page_obj.number,
                "empty_message": empty_message,
            },
            request=request,
        )

        return JsonResponse(
            {
                "html": html,
                "page": page_obj.number,
                "total_pages": paginator.num_pages,
                "count": paginator.count,
            }
        )


class MembroPromoverFormView(MembrosPromocaoPermissionMixin, LoginRequiredMixin, TemplateView):
    template_name = "membros/promover_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.organizacao = getattr(request.user, "organizacao", None)
        if self.organizacao is None:
            raise PermissionDenied(_("É necessário pertencer a uma organização para promover membros."))
        self.membro = get_object_or_404(
            User,
            pk=kwargs.get("pk"),
            organizacao=self.organizacao,
        )
        self.origin_section = self._resolve_origin_section(request)
        return super().dispatch(request, *args, **kwargs)

    def _resolve_origin_section(self, request) -> str:
        section = (request.GET.get("section") or request.POST.get("section") or "").strip()
        if section in MembroListDataMixin.sections:
            return section
        return ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(self._build_form_context(**kwargs))

        return context

    def post(self, request, *args, **kwargs):
        workflow_result = execute_promocao_from_post(
            membro=self.membro,
            organizacao=self.organizacao,
            post_data=request.POST,
        )

        if not workflow_result.success:
            context = self.get_context_data(
                selected_nucleado=workflow_result.selected_nucleado,
                selected_consultor=workflow_result.selected_consultor,
                selected_coordenador=workflow_result.selected_coordenador,
                selected_coordenador_roles=workflow_result.selected_coordenador_roles,
                selected_remover_nucleado=workflow_result.selected_remover_nucleado,
                selected_remover_consultor=workflow_result.selected_remover_consultor,
                selected_remover_coordenador=workflow_result.selected_remover_coordenador,
                form_errors=workflow_result.form_errors,
            )
            return self.render_to_response(context, status=400)

        context = self.get_context_data(
            selected_nucleado=[],
            selected_consultor=[],
            selected_coordenador=[],
            selected_coordenador_roles={},
            selected_remover_nucleado=[],
            selected_remover_consultor=[],
            selected_remover_coordenador=[],
            success_message=_("Promoção registrada com sucesso."),
            form_errors=[],
        )
        return self.render_to_response(context)

    def _build_form_context(self, **kwargs):
        return build_promocao_form_context(
            membro=self.membro,
            organizacao=self.organizacao,
            selected_nucleado=kwargs.get("selected_nucleado"),
            selected_consultor=kwargs.get("selected_consultor"),
            selected_coordenador=kwargs.get("selected_coordenador"),
            selected_coordenador_roles=kwargs.get("selected_coordenador_roles"),
            selected_remover_nucleado=kwargs.get("selected_remover_nucleado"),
            selected_remover_consultor=kwargs.get("selected_remover_consultor"),
            selected_remover_coordenador=kwargs.get("selected_remover_coordenador"),
            form_errors=kwargs.get("form_errors"),
            success_message=kwargs.get("success_message"),
            origin_section=getattr(self, "origin_section", ""),
        )

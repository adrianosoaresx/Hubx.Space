from __future__ import annotations

from collections.abc import Iterable

from django.db import transaction

from nucleos.models import Nucleo, ParticipacaoNucleo


def apply_promocao_persistence(
    *,
    membro,
    organizacao,
    valid_action_ids: set[int],
    valid_ids: set[int],
    valid_consultor_ids: set[int],
    nucleado_ids: Iterable[int],
    coordenador_roles: dict[int, str],
    remover_nucleado_ids: Iterable[int],
    remover_consultor_ids: Iterable[int],
    remover_coordenador_ids: Iterable[int],
) -> None:
    nucleado_set = set(nucleado_ids)
    remover_nucleado_set = set(remover_nucleado_ids)
    remover_consultor_set = set(remover_consultor_ids)
    remover_coordenador_set = set(remover_coordenador_ids)

    with transaction.atomic():
        nucleos_queryset = {
            nucleo.id: nucleo
            for nucleo in Nucleo.objects.filter(
                organizacao=organizacao,
                id__in=valid_action_ids,
            ).select_for_update()
        }

        participacoes_map = {
            participacao.nucleo_id: participacao
            for participacao in ParticipacaoNucleo.objects.select_for_update().filter(
                user=membro, nucleo_id__in=valid_action_ids
            )
        }

        for nucleo_id in remover_consultor_set & valid_action_ids:
            nucleo = nucleos_queryset.get(nucleo_id)
            if nucleo and nucleo.consultor_id == membro.pk:
                nucleo.consultor = None
                nucleo.save(update_fields=["consultor"])

        if valid_consultor_ids:
            for nucleo_id in valid_consultor_ids:
                nucleo = nucleos_queryset.get(nucleo_id)
                if not nucleo:
                    continue
                if nucleo.consultor_id != membro.pk:
                    nucleo.consultor = membro
                    nucleo.save(update_fields=["consultor"])

        for nucleo_id in valid_ids:
            nucleo = nucleos_queryset.get(nucleo_id)
            if not nucleo:
                continue
            assign_coordenador = nucleo_id in coordenador_roles
            assign_nucleado = nucleo_id in nucleado_set
            if not assign_coordenador and not assign_nucleado:
                continue
            participacao = participacoes_map.get(nucleo_id)
            if not participacao:
                participacao = ParticipacaoNucleo.objects.create(
                    nucleo=nucleo,
                    user=membro,
                    status="ativo",
                )
                participacoes_map[nucleo_id] = participacao

            update_fields: set[str] = set()
            if participacao.status != "ativo":
                participacao.status = "ativo"
                update_fields.add("status")
            if participacao.status_suspensao:
                participacao.status_suspensao = False
                update_fields.add("status_suspensao")
            if assign_coordenador:
                if participacao.papel != "coordenador":
                    participacao.papel = "coordenador"
                    update_fields.add("papel")
                novo_papel = coordenador_roles.get(nucleo_id)
                if participacao.papel_coordenador != novo_papel:
                    participacao.papel_coordenador = novo_papel
                    update_fields.add("papel_coordenador")
            elif assign_nucleado and participacao.papel != "coordenador":
                if participacao.papel != "membro":
                    participacao.papel = "membro"
                    update_fields.add("papel")
                if participacao.papel_coordenador:
                    participacao.papel_coordenador = None
                    update_fields.add("papel_coordenador")
            if update_fields:
                participacao.save(update_fields=list(update_fields))

        for nucleo_id in remover_coordenador_set & valid_action_ids:
            participacao = participacoes_map.get(nucleo_id)
            if not participacao or participacao.papel != "coordenador":
                continue
            update_fields: set[str] = set()
            if participacao.papel != "membro":
                participacao.papel = "membro"
                update_fields.add("papel")
            if participacao.papel_coordenador:
                participacao.papel_coordenador = None
                update_fields.add("papel_coordenador")
            if participacao.status != "ativo":
                participacao.status = "ativo"
                update_fields.add("status")
            if participacao.status_suspensao:
                participacao.status_suspensao = False
                update_fields.add("status_suspensao")
            if update_fields:
                participacao.save(update_fields=list(update_fields))

        for nucleo_id in remover_nucleado_set & valid_action_ids:
            participacao = participacoes_map.get(nucleo_id)
            if not participacao:
                continue
            update_fields: set[str] = set()
            if participacao.status != "inativo":
                participacao.status = "inativo"
                update_fields.add("status")
            if participacao.papel != "membro":
                participacao.papel = "membro"
                update_fields.add("papel")
            if participacao.papel_coordenador:
                participacao.papel_coordenador = None
                update_fields.add("papel_coordenador")
            if participacao.status_suspensao:
                participacao.status_suspensao = False
                update_fields.add("status_suspensao")
            if update_fields:
                participacao.save(update_fields=list(update_fields))

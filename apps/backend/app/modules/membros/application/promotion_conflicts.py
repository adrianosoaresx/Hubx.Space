from __future__ import annotations

from collections import defaultdict

from django.utils.translation import gettext_lazy as _

from nucleos.models import Nucleo, ParticipacaoNucleo


def validate_promocao_conflicts(
    *,
    membro,
    coordenador_ids: list[int],
    coordenador_roles: dict[int, str],
    valid_action_ids: set[int],
    nucleado_ids: list[int],
    consultor_ids: list[int],
    remover_nucleado_ids: list[int],
    remover_consultor_ids: list[int],
    remover_coordenador_ids: list[int],
) -> tuple[list[str], set[int]]:
    errors: list[str] = []
    papel_choices = {value for value, _ in ParticipacaoNucleo.PapelCoordenador.choices}

    for nucleo_id in coordenador_ids:
        papel = (coordenador_roles.get(nucleo_id) or "").strip()
        if not papel:
            errors.append(_("Selecione um papel de coordenação para cada núcleo escolhido."))
            return errors, {nid for nid in consultor_ids if nid in valid_action_ids}
        if papel not in papel_choices:
            errors.append(_("Selecione um papel de coordenação válido."))
            return errors, {nid for nid in consultor_ids if nid in valid_action_ids}

    role_labels = dict(ParticipacaoNucleo.PapelCoordenador.choices)
    valid_coordenador_ids = {nid for nid in coordenador_roles.keys() if nid in valid_action_ids}

    if valid_coordenador_ids:
        ocupados = (
            ParticipacaoNucleo.objects.filter(
                nucleo_id__in=valid_coordenador_ids,
                papel="coordenador",
                status="ativo",
                papel_coordenador__in=set(coordenador_roles.values()),
            )
            .exclude(user=membro)
            .select_related("user", "nucleo")
        )
        for participacao in ocupados:
            papel = participacao.papel_coordenador
            if papel and coordenador_roles.get(participacao.nucleo_id) == papel:
                errors.append(
                    _("O papel %(papel)s do núcleo %(nucleo)s já está ocupado por %(nome)s.")
                    % {
                        "papel": role_labels.get(papel, papel),
                        "nucleo": participacao.nucleo.nome,
                        "nome": participacao.user.display_name or participacao.user.username,
                    }
                )

        restricted_roles = {
            ParticipacaoNucleo.PapelCoordenador.COORDENADOR_GERAL,
            ParticipacaoNucleo.PapelCoordenador.VICE_COORDENADOR,
        }
        selected_by_role: defaultdict[str, set[int]] = defaultdict(set)
        for nucleo_id, papel in coordenador_roles.items():
            if nucleo_id in valid_coordenador_ids:
                selected_by_role[papel].add(nucleo_id)

        existentes: defaultdict[str, set[int]] = defaultdict(set)
        existentes_qs = ParticipacaoNucleo.objects.filter(
            user=membro,
            papel="coordenador",
            status="ativo",
            papel_coordenador__in=restricted_roles,
        ).values_list("papel_coordenador", "nucleo_id")
        for papel, nucleo_id in existentes_qs:
            existentes[papel].add(nucleo_id)

        for papel in restricted_roles:
            novos = selected_by_role.get(papel, set())
            if not novos:
                continue
            atuais = existentes.get(papel, set())
            novos_diferentes = {nid for nid in novos if nid not in atuais}
            if atuais and novos_diferentes:
                errors.append(
                    _("%(papel)s não pode ser atribuído a múltiplos núcleos diferentes.")
                    % {"papel": role_labels.get(papel, papel)}
                )
            elif not atuais and len(novos_diferentes) > 1:
                errors.append(
                    _("Selecione apenas um núcleo para o papel %(papel)s.")
                    % {"papel": role_labels.get(papel, papel)}
                )

    if set(nucleado_ids) & set(remover_nucleado_ids):
        errors.append(
            _("Não é possível promover e remover a participação de nucleado no mesmo núcleo.")
        )
    if set(consultor_ids) & set(remover_consultor_ids):
        errors.append(_("Não é possível promover e remover a consultoria do mesmo núcleo."))
    if set(coordenador_ids) & set(remover_coordenador_ids):
        errors.append(_("Não é possível promover e remover a coordenação no mesmo núcleo."))
    if set(consultor_ids) & set(coordenador_ids):
        errors.append(_("Selecione apenas uma opção de promoção por núcleo."))

    valid_consultor_ids = {nid for nid in consultor_ids if nid in valid_action_ids}
    if valid_consultor_ids and not errors:
        consultores_ocupados = (
            Nucleo.objects.filter(id__in=valid_consultor_ids)
            .exclude(consultor__isnull=True)
            .exclude(consultor=membro)
            .select_related("consultor")
        )
        for nucleo in consultores_ocupados:
            errors.append(
                _("O núcleo %(nucleo)s já possui o consultor %(nome)s.")
                % {
                    "nucleo": nucleo.nome,
                    "nome": nucleo.consultor.display_name or nucleo.consultor.username,
                }
            )

    if remover_nucleado_ids and not errors:
        coordenador_ativos = set(
            ParticipacaoNucleo.objects.filter(
                user=membro,
                nucleo_id__in=remover_nucleado_ids,
                status="ativo",
                papel="coordenador",
            ).values_list("nucleo_id", flat=True)
        )
        bloqueados = coordenador_ativos - set(remover_coordenador_ids)
        if bloqueados:
            nomes = dict(Nucleo.objects.filter(id__in=bloqueados).values_list("id", "nome"))
            for nucleo_id in bloqueados:
                errors.append(
                    _("Remova a coordenação do núcleo %(nucleo)s antes de remover a participação.")
                    % {"nucleo": nomes.get(nucleo_id, nucleo_id)}
                )

    return errors, valid_consultor_ids

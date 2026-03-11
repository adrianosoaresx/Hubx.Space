from __future__ import annotations

from eventos.models import BriefingEvento


def get_evento_briefing(evento):
    return getattr(evento, "briefing", None)


def build_briefing_select_initial(evento, *, form_is_bound: bool) -> dict[str, int]:
    if form_is_bound:
        return {}
    briefing = get_evento_briefing(evento)
    if briefing and briefing.template_id:
        return {"template": briefing.template_id}
    return {}


def apply_briefing_template_selection(evento, template):
    briefing = get_evento_briefing(evento)
    if briefing is None:
        created = BriefingEvento.objects.create(evento=evento, template=template)
        return created

    if briefing.template_id != template.id:
        briefing.respostas = {}
    briefing.template = template
    briefing.save(update_fields=["template", "respostas", "updated_at"])
    return briefing

from __future__ import annotations

from django.utils import timezone

from tokens.models import TokenAcesso
from tokens.services import create_invite_token

from eventos.models import PreRegistroConvite


def get_public_invite_token_generator(evento, user_model):
    if getattr(evento, "organizacao", None) and evento.organizacao.created_by:
        return evento.organizacao.created_by

    staff_user = user_model.objects.filter(is_staff=True).order_by("id").first()
    if staff_user:
        return staff_user

    return user_model.objects.filter(is_superuser=True).order_by("id").first()


def is_public_invite_token_reusable(preregistro, now=None) -> bool:
    if preregistro is None:
        return False
    now = now or timezone.now()
    token = preregistro.token
    if token.estado != TokenAcesso.Estado.NOVO:
        return False
    if token.data_expiracao and token.data_expiracao <= now:
        return False
    return True


def create_public_invite_token(evento, email: str, user_model):
    generator = get_public_invite_token_generator(evento=evento, user_model=user_model)
    if generator is None:
        return None, None

    preregistro = (
        PreRegistroConvite.objects.filter(email__iexact=email, evento=evento)
        .select_related("token")
        .first()
    )
    if is_public_invite_token_reusable(preregistro):
        return preregistro, preregistro.codigo

    token, codigo = create_invite_token(
        gerado_por=generator,
        tipo_destino=TokenAcesso.TipoUsuario.CONVIDADO.value,
        organizacao=evento.organizacao,
    )

    preregistro, _ = PreRegistroConvite.objects.update_or_create(
        email=email,
        evento=evento,
        defaults={
            "token": token,
            "codigo": codigo,
            "status": PreRegistroConvite.Status.PENDENTE,
        },
    )
    return preregistro, codigo

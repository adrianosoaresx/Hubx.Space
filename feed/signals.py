from __future__ import annotations

from django.conf import settings
from django.core.cache import cache
import logging
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from notificacoes.services.notificacoes import enviar_para_usuario

from .models import Comment, Like, Post
from .tasks import notificar_autor_sobre_interacao


@receiver(post_save, sender=Like)
def notificar_like(sender, instance, created, **kwargs):
    if created:
        try:
            enviar_para_usuario(
                instance.post.autor,
                "feed_like",
                {"post_id": str(instance.post.id)},
            )
        except Exception as exc:  # pragma: no cover - melhor esforço
            logging.exception(exc)
        if getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False):
            notificar_autor_sobre_interacao(instance.post_id, "like")
        else:
            notificar_autor_sobre_interacao.delay(instance.post_id, "like")


@receiver(post_save, sender=Comment)
def notificar_comment(sender, instance, created, **kwargs):
    if created:
        try:
            enviar_para_usuario(
                instance.post.autor,
                "feed_comment",
                {"post_id": str(instance.post.id)},
            )
        except Exception as exc:  # pragma: no cover - melhor esforço
            logging.exception(exc)
        if getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False):
            notificar_autor_sobre_interacao(instance.post_id, "comment")
        else:
            notificar_autor_sobre_interacao.delay(instance.post_id, "comment")


@receiver([post_save, post_delete], sender=Post)
def limpar_cache_feed(**_kwargs) -> None:
    """Remove entradas de cache após alterações em posts."""
    try:
        # Preferir limpar somente chaves do feed quando possível
        if hasattr(cache, "delete_pattern"):
            cache.delete_pattern("feed:*")  # type: ignore[attr-defined]
        else:
            cache.clear()
    except Exception:  # pragma: no cover - melhor esforço
        # Evita que falhas na limpeza de cache quebrem o fluxo principal
        logging.getLogger(__name__).exception("Falha ao limpar cache do feed")

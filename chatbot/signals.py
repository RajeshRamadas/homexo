"""
chatbot/signals.py
───────────────────
Auto-embeds a Property into pgvector whenever it is saved.

Rules:
  • Property saved with status='active'  →  create/update embedding
  • Property saved with any other status →  delete embedding (if exists)

The embedding runs in a background thread so it never slows down
an admin save or API call.
"""

import logging
import threading

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def _embed_in_background(prop_pk: int) -> None:
    """Run inside a daemon thread — embed one property by PK."""
    try:
        from properties.models import Property
        from chatbot.models import PropertyEmbedding
        from chatbot.rag.embedder import embed_property

        prop = (
            Property.objects
            .prefetch_related('features', 'connectivity', 'images')
            .select_related('developer')
            .get(pk=prop_pk)
        )

        vec  = embed_property(prop)
        text = (
            f'{prop.title} | {prop.locality}, {prop.city} | '
            f'{prop.display_price} | {prop.get_bhk_display() if prop.bhk else ""}'
        )

        obj, created = PropertyEmbedding.objects.update_or_create(
            property=prop,
            defaults={'source_text': text, 'embedding': vec},
        )
        action = 'Created' if created else 'Updated'
        logger.info('Auto-embed: %s embedding for "%s" (pk=%s)', action, prop.title, prop_pk)

    except Exception as exc:
        logger.error('Auto-embed failed for property pk=%s: %s', prop_pk, exc, exc_info=True)


def _delete_embedding(prop_pk: int) -> None:
    """Remove any existing embedding for a deactivated/deleted property."""
    try:
        from chatbot.models import PropertyEmbedding
        deleted, _ = PropertyEmbedding.objects.filter(property_id=prop_pk).delete()
        if deleted:
            logger.info('Auto-embed: removed embedding for property pk=%s', prop_pk)
    except Exception as exc:
        logger.error('Auto-embed delete failed for property pk=%s: %s', prop_pk, exc, exc_info=True)


@receiver(post_save, sender='properties.Property')
def property_post_save(sender, instance, **kwargs):
    """
    Trigger embedding whenever a Property is saved.
      - status == 'active'  →  embed (background thread)
      - any other status    →  remove embedding
    """
    if instance.status == 'active':
        t = threading.Thread(
            target=_embed_in_background,
            args=(instance.pk,),
            daemon=True,
        )
        t.start()
    else:
        # Property deactivated / taken off market — remove stale embedding
        t = threading.Thread(
            target=_delete_embedding,
            args=(instance.pk,),
            daemon=True,
        )
        t.start()


@receiver(post_delete, sender='properties.Property')
def property_post_delete(sender, instance, **kwargs):
    """Clean up the embedding when a property is hard-deleted."""
    t = threading.Thread(
        target=_delete_embedding,
        args=(instance.pk,),
        daemon=True,
    )
    t.start()

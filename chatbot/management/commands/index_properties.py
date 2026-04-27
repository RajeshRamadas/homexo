"""
Management command: index_properties
─────────────────────────────────────
Generates sentence-transformer embeddings for all active Property records
and stores them in chatbot_propertyembedding (the vector column).

Usage:
    python manage.py index_properties            # new/unembedded only
    python manage.py index_properties --force    # re-embed everything
    python manage.py index_properties --id 42    # single property
"""

import logging
from django.core.management.base import BaseCommand
from properties.models import Property
from chatbot.models import PropertyEmbedding
from chatbot.rag.embedder import embed_property

logger = logging.getLogger(__name__)
BATCH_SIZE = 64


class Command(BaseCommand):
    help = 'Embed active property listings into pgvector (all-MiniLM-L6-v2)'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true',
                            help='Re-embed already-indexed properties')
        parser.add_argument('--id', type=int, dest='property_id',
                            help='Index only property with this ID')

    def handle(self, *args, **options):
        force   = options['force']
        prop_id = options['property_id']

        qs = Property.objects.filter(status='active') \
                     .prefetch_related('features', 'connectivity', 'images') \
                     .select_related('developer')

        if prop_id:
            qs = qs.filter(pk=prop_id)

        if not force:
            already = PropertyEmbedding.objects.values_list('property_id', flat=True)
            qs = qs.exclude(pk__in=already)

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS('✓ All properties already indexed.'))
            return

        self.stdout.write(f'🔄 Indexing {total} propert{"y" if total==1 else "ies"}...')
        success = errors = 0
        batch   = []

        for i, prop in enumerate(qs.iterator(chunk_size=BATCH_SIZE), 1):
            try:
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
                self.stdout.write(f'  [{i}/{total}] {action}: {prop.title}')
                success += 1
            except Exception as e:
                errors += 1
                self.stderr.write(f'  [{i}/{total}] ERROR "{prop.title}": {e}')

        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Done — {success} indexed, {errors} errors.')
        )

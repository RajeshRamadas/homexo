"""
Management command: cleanup_rejected_listings

Permanently deletes rejected properties whose auto_delete_at timestamp
has passed (i.e. older than 30 days since rejection).

Run daily via cron:
    0 2 * * * /path/to/venv/bin/python /path/to/manage.py cleanup_rejected_listings
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from properties.models import Property


class Command(BaseCommand):
    help = 'Delete rejected property listings that have passed their 30-day grace period.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting.',
        )

    def handle(self, *args, **options):
        now     = timezone.now()
        dry_run = options['dry_run']

        expired = Property.objects.filter(
            status='rejected',
            auto_delete_at__lte=now,
        )

        count = expired.count()
        if count == 0:
            self.stdout.write('No expired rejected listings found.')
            return

        for prop in expired:
            self.stdout.write(
                f'  {"[DRY RUN] Would delete" if dry_run else "Deleting"}: '
                f'"{prop.title}" (rejected {prop.rejected_at.strftime("%d %b %Y")}, '
                f'deadline {prop.auto_delete_at.strftime("%d %b %Y")})'
            )

        if not dry_run:
            expired.delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {count} expired rejected listing(s).'))
        else:
            self.stdout.write(self.style.WARNING(f'Dry run: {count} listing(s) would be deleted.'))

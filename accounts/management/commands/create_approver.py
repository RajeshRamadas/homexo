"""
Management command: create_approver
Creates (or updates) the approver@homexo.in account with the APPROVER role.

Usage:
    python manage.py create_approver --password <password>
"""

import secrets
import string
from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Create the approver@homexo.in account with Property Approver role.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            type=str,
            default=None,
            help='Password for the approver account. A random one is generated if not supplied.',
        )

    def handle(self, *args, **options):
        email = 'approver@homexo.in'
        password = options['password']

        if not password:
            alphabet = string.ascii_letters + string.digits + '!@#$%'
            password = ''.join(secrets.choice(alphabet) for _ in range(16))
            generated = True
        else:
            generated = False

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': 'Property',
                'last_name': 'Approver',
                'role': User.Role.APPROVER,
                'is_active': True,
                'is_verified': True,
                'is_staff': False,
            },
        )

        if not created:
            # Update role if account already existed
            user.role = User.Role.APPROVER
            user.is_active = True
            user.save(update_fields=['role', 'is_active'])
            self.stdout.write(self.style.WARNING(f'Account already existed — role updated to APPROVER.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Created account: {email}'))

        user.set_password(password)
        user.save(update_fields=['password'])

        if generated:
            self.stdout.write(self.style.SUCCESS(f'  Generated password : {password}'))
            self.stdout.write(self.style.WARNING('  Save this password — it will not be shown again.'))
        else:
            self.stdout.write(self.style.SUCCESS('  Password set successfully.'))

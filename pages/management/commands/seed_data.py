"""
pages/management/commands/seed_data.py

Run with: python manage.py seed_data

Creates:
  - 1 superuser
  - 10 property listings (mix of featured, signature, buy/rent)
  - 3 testimonials
  - 3 blog posts
  - 5 property tags
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with sample HOMEXO data'

    def handle(self, *args, **options):
        self.stdout.write('🏠 Seeding HOMEXO data...\n')

        # ── Super user ────────────────────────────────────────────────────────
        if not User.objects.filter(email='admin@homexo.in').exists():
            User.objects.create_superuser(
                email='admin@homexo.in',
                password='admin123',
                first_name='Admin',
                last_name='HOMEXO',
                role='admin',
            )
            self.stdout.write(self.style.SUCCESS('  ✓ Superuser created: admin@homexo.in / admin123'))

        # ── Tags ──────────────────────────────────────────────────────────────
        from properties.models import PropertyTag
        tags_data = ['Pool', 'Gym', 'Clubhouse', 'Garden', 'Sea View', 'Gated Community', 'Power Backup']
        tags = {}
        for name in tags_data:
            tag, _ = PropertyTag.objects.get_or_create(name=name)
            tags[name] = tag
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(tags)} tags created'))

        # ── Properties ────────────────────────────────────────────────────────
        from properties.models import Property
        props_data = [
            {'title': 'The Celestia Sky Estate', 'type': 'buy', 'ptype': 'villa',
             'price': 22_00_00_000, 'locality': 'Sadashivanagar', 'beds': 6, 'baths': 5, 'sqft': 9200,
             'featured': True, 'signature': True, 'price_label': '/ Upwards',
             'desc': 'An architectural masterpiece nestled in the heart of Bengaluru\'s most prestigious neighbourhood.'},
            {'title': 'The Meridian Penthouse', 'type': 'buy', 'ptype': 'penthouse',
             'price': 4_20_00_000, 'locality': 'Whitefield', 'beds': 4, 'baths': 3, 'sqft': 3800,
             'featured': True, 'signature': False, 'price_label': '/ Onwards',
             'desc': 'Sky-high luxury living with panoramic city views from every room.'},
            {'title': 'Amber Heights', 'type': 'buy', 'ptype': 'apartment',
             'price': 7_40_00_000, 'locality': 'Hebbal', 'beds': 4, 'baths': 3, 'sqft': 4200,
             'featured': False, 'signature': True, 'price_label': '',
             'desc': 'Premium lake-view apartments with world-class amenities.'},
            {'title': 'Emerald Grove Villa', 'type': 'buy', 'ptype': 'villa',
             'price': 12_80_00_000, 'locality': 'Yelahanka', 'beds': 5, 'baths': 4, 'sqft': 6500,
             'featured': True, 'signature': True, 'price_label': '',
             'desc': 'Sprawling villa surrounded by lush greenery in North Bengaluru.'},
            {'title': 'Azure Skyline Tower', 'type': 'buy', 'ptype': 'apartment',
             'price': 2_80_00_000, 'locality': 'Electronic City', 'beds': 3, 'baths': 2, 'sqft': 1850,
             'featured': True, 'signature': False, 'price_label': '',
             'desc': 'Smart homes designed for the modern professional.'},
            {'title': 'The Royal Enclave', 'type': 'rent', 'ptype': 'apartment',
             'price': 1_20_000, 'locality': 'Koramangala', 'beds': 3, 'baths': 2, 'sqft': 2200,
             'featured': True, 'signature': False, 'price_label': '/ Month',
             'desc': 'Fully furnished premium apartment in the heart of Koramangala.'},
            {'title': 'Prestige Garden Suites', 'type': 'rent', 'ptype': 'apartment',
             'price': 75_000, 'locality': 'Indiranagar', 'beds': 2, 'baths': 2, 'sqft': 1400,
             'featured': True, 'signature': False, 'price_label': '/ Month',
             'desc': 'Elegant 2BHK apartment steps away from Indiranagar\'s best cafes.'},
            {'title': 'Tech Corridor Office Park', 'type': 'commercial', 'ptype': 'office',
             'price': 18_00_00_000, 'locality': 'Outer Ring Road', 'beds': 0, 'baths': 10, 'sqft': 25000,
             'featured': True, 'signature': False, 'price_label': '',
             'desc': 'Grade-A office space with dedicated parking and 24/7 security.'},
            {'title': 'Sunrise Boulevard Apartments', 'type': 'new_project', 'ptype': 'apartment',
             'price': 95_00_000, 'locality': 'Sarjapur Road', 'beds': 3, 'baths': 2, 'sqft': 1650,
             'featured': True, 'signature': False, 'price_label': '/ Onwards',
             'desc': 'Ready-to-move new project with RERA approved units.'},
            {'title': 'The Lakeview Manor', 'type': 'buy', 'ptype': 'villa',
             'price': 8_50_00_000, 'locality': 'Devanahalli', 'beds': 4, 'baths': 4, 'sqft': 5200,
             'featured': False, 'signature': False, 'price_label': '',
             'desc': 'Private villa with direct lake frontage — a rare find.'},
        ]

        import random
        created = 0
        for i, pd in enumerate(props_data):
            if not Property.objects.filter(title=pd['title']).exists():
                prop = Property.objects.create(
                    owner=User.objects.filter(role='admin').first(),
                    title=pd['title'],
                    listing_type=pd['type'],
                    property_type=pd['ptype'],
                    price=pd['price'],
                    price_label=pd.get('price_label', ''),
                    locality=pd['locality'],
                    city='Bengaluru',
                    state='Karnataka',
                    address=f'{pd["locality"]}, Bengaluru, Karnataka',
                    bedrooms=pd['beds'],
                    bathrooms=pd['baths'],
                    area_sqft=pd['sqft'],
                    description=pd['desc'],
                    is_featured=pd['featured'],
                    is_signature=pd['signature'],
                    is_new=True,
                    status='active',
                    bhk=f'{pd["beds"]}bhk' if pd['beds'] else '',
                    furnishing='semi',
                    parking_slots=2,
                )
                # Add random tags
                prop.tags.set(random.sample(list(tags.values()), k=min(3, len(tags))))
                created += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ {created} properties created'))

        # ── Testimonials ──────────────────────────────────────────────────────
        from testimonials.models import Testimonial
        testimonials_data = [
            {'name': 'Arjun Kapoor', 'loc': 'Whitefield, Bengaluru', 'rating': 5,
             'review': 'HOMEXO made finding our dream home effortless. The team truly understood our vision and delivered beyond expectations.'},
            {'name': 'Sneha & Vikram Nair', 'loc': 'Koramangala, Bengaluru', 'rating': 5,
             'review': 'Exceptional service from start to finish. Our agent Priya was knowledgeable, patient, and genuinely cared about finding us the right home.'},
            {'name': 'Ravi Teja', 'loc': 'Hyderabad', 'rating': 4,
             'review': 'The commercial property consultation was top-notch. HOMEXO\'s market intelligence helped us make the right investment decision.'},
        ]
        for td in testimonials_data:
            if not Testimonial.objects.filter(client_name=td['name']).exists():
                Testimonial.objects.create(**{
                    'client_name': td['name'], 'client_location': td['loc'],
                    'rating': td['rating'], 'review': td['review'], 'is_active': True
                })
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(testimonials_data)} testimonials created'))

        # ── Blog Posts ────────────────────────────────────────────────────────
        from blog.models import Post, Category
        from django.utils import timezone
        cat, _ = Category.objects.get_or_create(name='Market Reports', defaults={'color': '#4A90C4'})
        posts = [
            ('Bengaluru Luxury Real Estate: Q1 2026 Report', 'Bengaluru\'s luxury segment continues to surge with record transactions in Sadashivanagar and Whitefield.'),
            ('Top 5 Investment Hotspots in Bengaluru for 2026', 'From Devanahalli to Sarjapur Road, we identify the locations offering maximum ROI this year.'),
            ('Understanding RERA: A Buyer\'s Guide', 'Everything you need to know about RERA compliance and how it protects your property investment.'),
        ]
        admin = User.objects.filter(role='admin').first()
        for title, body in posts:
            if not Post.objects.filter(title=title).exists():
                Post.objects.create(
                    title=title, body=body, excerpt=body[:150],
                    category=cat, author=admin,
                    status='published', published_at=timezone.now()
                )
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(posts)} blog posts created'))

        self.stdout.write('\n' + self.style.SUCCESS('✅ Seed complete! Visit http://127.0.0.1:8000'))
        self.stdout.write(self.style.WARNING('   Admin: admin@homexo.in / admin123'))

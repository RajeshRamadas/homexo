# Seed the three standard segment tags: Luxury, Premium, Budget
from django.db import migrations


def seed_segment_tags(apps, schema_editor):
    PropertyTag = apps.get_model('properties', 'PropertyTag')
    tags = [
        {'name': 'Luxury',  'slug': 'luxury'},
        {'name': 'Premium', 'slug': 'premium'},
        {'name': 'Budget',  'slug': 'budget'},
    ]
    for tag_data in tags:
        PropertyTag.objects.get_or_create(slug=tag_data['slug'], defaults={'name': tag_data['name']})


def reverse_seed(apps, schema_editor):
    # Only remove if no properties are linked — safe rollback
    PropertyTag = apps.get_model('properties', 'PropertyTag')
    PropertyTag.objects.filter(slug__in=['luxury', 'premium', 'budget']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0024_property_video_url'),
    ]

    operations = [
        migrations.RunPython(seed_segment_tags, reverse_code=reverse_seed),
    ]

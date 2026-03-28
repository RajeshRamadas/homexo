from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0004_add_floor_plan_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertyfloorplan',
            name='bhk_type',
            field=models.CharField(
                blank=True,
                max_length=100,
                help_text='Config tab label, e.g. "2 BHK Apartment". Plans sharing the same bhk_type are grouped into one tab.',
            ),
        ),
        migrations.AddField(
            model_name='propertyfloorplan',
            name='size_sqft',
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                help_text='Size variant in sq.ft, shown as a sub-tab, e.g. 977 or 1040.',
            ),
        ),
        migrations.AddField(
            model_name='propertyfloorplan',
            name='price_display',
            field=models.CharField(
                blank=True,
                max_length=100,
                help_text='Price label for this variant, e.g. "\u20b9 92.95 L" or "\u20b9 1.05 Cr".',
            ),
        ),
        migrations.AddField(
            model_name='propertyfloorplan',
            name='room_data',
            field=models.JSONField(
                blank=True,
                null=True,
                help_text='Room dimensions as JSON: [{"title": "Bedroom 1", "val": "11\'0 \xd7 11\'2"}, ...]',
            ),
        ),
    ]

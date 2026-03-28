from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0005_floorplan_bhk_size_price_roomdata'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertyfloorplan',
            name='image_3d',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='properties/floor_plans/',
                help_text='Optional 3D render of the same layout. When present, a 2D/3D toggle will appear on the viewer.',
            ),
        ),
    ]

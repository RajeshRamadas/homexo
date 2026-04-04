from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0003_add_ownership_rera'),
    ]

    operations = [
        # Remove the old single floor_plan field from Property
        migrations.RemoveField(
            model_name='property',
            name='floor_plan',
        ),
        # Add the new PropertyFloorPlan model for multiple images
        migrations.CreateModel(
            name='PropertyFloorPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='properties/floor_plans/')),
                ('caption', models.CharField(blank=True, max_length=200)),
                ('order', models.PositiveSmallIntegerField(default=0)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                               related_name='floor_plans', to='properties.property')),
            ],
            options={
                'verbose_name': 'Floor Plan',
                'verbose_name_plural': 'Floor Plans',
                'ordering': ['order', 'id'],
            },
        ),
    ]

"""
chatbot/migrations/0001_initial.py
"""
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('properties', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(db_index=True, max_length=128, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                           related_name='chat_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Chat Session',
                'verbose_name_plural': 'Chat Sessions',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('user', 'User'), ('assistant', 'Assistant')], max_length=10)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                              related_name='messages', to='chatbot.chatsession')),
            ],
            options={
                'verbose_name': 'Chat Message',
                'verbose_name_plural': 'Chat Messages',
                'ordering': ['created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='chatmessage',
            index=models.Index(fields=['session', 'created_at'], name='chatbot_chatmessage_session_created_idx'),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(db_index=True, max_length=128, unique=True)),
                ('budget_min', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ('budget_max', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ('preferred_locations', models.JSONField(blank=True, default=list)),
                ('property_type', models.CharField(blank=True, max_length=64)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'User Profile',
                'verbose_name_plural': 'User Profiles',
            },
        ),
        migrations.CreateModel(
            name='PropertyEmbedding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_text', models.TextField(blank=True)),
                ('embedding', models.TextField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('property', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                                                  related_name='embedding', to='properties.property')),
            ],
            options={
                'verbose_name': 'Property Embedding',
                'verbose_name_plural': 'Property Embeddings',
            },
        ),
    ]

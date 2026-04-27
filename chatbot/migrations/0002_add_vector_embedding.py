"""
chatbot/migrations/0002_add_vector_embedding.py
─────────────────────────────────────────────────
PostgreSQL-only operations:
  1. Enable pgvector extension
  2. Convert embedding TEXT → vector(384)
  3. Create IVFFlat cosine index

Safely skipped on SQLite (dev without Postgres).
"""
from django.db import migrations


def enable_pgvector(apps, schema_editor):
    """Enable vector extension — PostgreSQL only."""
    if schema_editor.connection.vendor != 'postgresql':
        return
    schema_editor.execute("CREATE EXTENSION IF NOT EXISTS vector;")


def convert_to_vector(apps, schema_editor):
    """Convert the embedding column from TEXT to vector(384) — PostgreSQL only."""
    if schema_editor.connection.vendor != 'postgresql':
        return
    schema_editor.execute("""
        ALTER TABLE chatbot_propertyembedding
            ALTER COLUMN embedding TYPE vector(384)
            USING NULL;
    """)


def revert_to_text(apps, schema_editor):
    """Reverse: convert vector(384) back to TEXT — PostgreSQL only."""
    if schema_editor.connection.vendor != 'postgresql':
        return
    schema_editor.execute("""
        ALTER TABLE chatbot_propertyembedding
            ALTER COLUMN embedding TYPE text USING NULL;
    """)


def create_ivfflat_index(apps, schema_editor):
    """Create IVFFlat cosine index — PostgreSQL only."""
    if schema_editor.connection.vendor != 'postgresql':
        return
    schema_editor.execute("""
        CREATE INDEX IF NOT EXISTS chatbot_embedding_ivfflat_idx
        ON chatbot_propertyembedding
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 10);
    """)


def drop_ivfflat_index(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    schema_editor.execute("DROP INDEX IF EXISTS chatbot_embedding_ivfflat_idx;")


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(enable_pgvector,    migrations.RunPython.noop),
        migrations.RunPython(convert_to_vector,  revert_to_text),
        migrations.RunPython(create_ivfflat_index, drop_ivfflat_index),
    ]

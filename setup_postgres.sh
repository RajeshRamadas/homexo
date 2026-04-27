#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# setup_postgres.sh
# Sets up the Homexo PostgreSQL database with pgvector extension.
# Run as: bash setup_postgres.sh
# ─────────────────────────────────────────────────────────────────────────────
set -e

DB_NAME="homexo_db"
DB_USER="homexo_user"
DB_PASS="homexo_secret"

echo "🐘 Setting up PostgreSQL for Homexo..."

# 1. Install pgvector extension (requires postgresql-16-pgvector package)
echo "📦 Installing postgresql-16-pgvector..."
sudo apt-get install -y postgresql-16-pgvector

# 2. Create database and user
echo "🗄️  Creating database and user..."
sudo -u postgres psql <<SQL
-- Create user if not exists
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$DB_USER') THEN
    CREATE ROLE $DB_USER WITH LOGIN PASSWORD '$DB_PASS';
  END IF;
END
\$\$;

-- Create database if not exists
SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
SQL

# 3. Enable pgvector extension
echo "🔌 Enabling pgvector extension..."
sudo -u postgres psql -d "$DB_NAME" <<SQL
CREATE EXTENSION IF NOT EXISTS vector;
-- Verify
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
SQL

echo ""
echo "✅ PostgreSQL setup complete!"
echo ""
echo "   Database : $DB_NAME"
echo "   User     : $DB_USER"
echo "   Password : $DB_PASS"
echo ""
echo "Next steps:"
echo "  1. Run: python manage.py migrate"
echo "  2. Run: python manage.py createsuperuser"
echo "  3. Run: python manage.py loaddata <your-fixtures>   (if you have data)"
echo "  4. Add your OPENAI_API_KEY to .env"
echo "  5. Run: python manage.py index_properties"

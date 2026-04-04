#!/bin/sh
set -e

echo "==> Waiting for database..."
until python -c "
import os, sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homexo.settings')
django.setup()
from django.db import connections
connections['default'].ensure_connection()
print('Database is ready.')
" 2>/dev/null; do
  echo "   Database unavailable, retrying in 2s..."
  sleep 2
done

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Starting application..."
exec "$@"

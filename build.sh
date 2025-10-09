#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "=== Starting deployment ==="
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create staticfiles directory if it doesn't exist
mkdir -p staticfiles

# Create database directory if it doesn't exist
mkdir -p $(dirname /opt/render/project/src/db.sqlite3) 2>/dev/null || true

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations - FORCE CREATE TABLES
echo "=== Applying database migrations ==="
python manage.py makemigrations --no-input
python manage.py migrate --no-input

echo "=== Checking database tables ==="
python manage.py shell -c "
from django.db import connection
tables = connection.introspection.table_names()
print('Database tables:', tables)
"


# Apply any outstanding database migrations
python manage.py migrate

echo "=== Deployment completed ==="
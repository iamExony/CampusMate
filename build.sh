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

# Collect static files with force if needed
python manage.py collectstatic --no-input --clear


# Apply any outstanding database migrations
python manage.py migrate

echo "=== Deployment completed ==="
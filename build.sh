#!/usr/bin/env bash
# Exit on error
set -o errexit

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate
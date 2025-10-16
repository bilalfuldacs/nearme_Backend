#!/usr/bin/env bash
# Render build script
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate

echo "Populating categories..."
python manage.py populate_categories

echo "Build complete!"


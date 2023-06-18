#!/bin/bash

# Django app starter script

set -o errexit
set -o pipefail
set -o nounset

cd martini

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py makemigrations
python manage.py migrate

# Start server
echo "Starting server"
exec gunicorn config.asgi:application --bind 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker

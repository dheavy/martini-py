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

# Create superuser
echo "Creating superuser"
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='$APP_SUPERUSER_NAME').exists() or User.objects.create_superuser('$APP_SUPERUSER_NAME', '$APP_SUPERUSER_EMAIL', '$APP_SUPERUSER_PWD')"

# Start server
echo "Starting server"
exec gunicorn config.asgi:application --bind 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker

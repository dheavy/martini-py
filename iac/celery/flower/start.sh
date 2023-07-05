#!/bin/bash

set -o errexit
set -o nounset

# Assuming that this script is located at 'iac/celery/beat/start.bash',
# and the Django project root is at the 'martini' directory, this helps
# the celery beat process find the apps' modules and settings
export PYTHONPATH=/app/martini:${PYTHONPATH:-}

worker_ready() {
    celery -A celery inspect ping
}

until worker_ready; do
  >&2 echo 'Celery workers not available'
  sleep 1
done
>&2 echo 'Celery workers available'

celery --app=config.celery:celery --broker="${CELERY_BROKER_URL}" flower

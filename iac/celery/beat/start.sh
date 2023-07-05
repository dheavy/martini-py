#!/bin/bash

set -o errexit
set -o nounset

# Assuming that this script is located at 'iac/celery/beat/start.bash',
# and the Django project root is at the 'martini' directory, this helps
# the celery beat process find the apps' modules and settings
export PYTHONPATH=/app/martini:${PYTHONPATH:-}

rm -f './celerybeat.pid'
celery -A config.celery:celery beat -l info

#!/bin/bash
set -a
source ../.env
set +a

# Run Django manage.py commands
python manage.py "$@"

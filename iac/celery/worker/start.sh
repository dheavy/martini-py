#!/bin/bash

set -o errexit
set -o nounset

# watchfiles \
#   --filter python \
#   'celery -A celery worker --loglevel=info'
celery -A celery worker

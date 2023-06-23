#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

postgres_ready() {
python << END
import sys

import psycopg2
import os

try:
    psycopg2.connect(
        dbname=os.environ['POSTGRES_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD'],
        host=os.environ['POSTGRES_HOST'],
        port=os.environ['POSTGRES_PORT']
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)

END
}

qdrant_ready() {
python << END
import sys
import requests
import os

QDRANT_URL = os.environ['QDRANT_URL']

try:
    response = requests.get(f"{QDRANT_URL}/collections")
    if response.status_code != 200:
        sys.exit(-1)
except Exception:
    sys.exit(-1)

sys.exit(0)

END
}

until postgres_ready; do
  >&2 echo 'Waiting for PostgreSQL to become available...'
  sleep 1
done
>&2 echo 'PostgreSQL is available'

until qdrant_ready; do
  >&2 echo 'Waiting for Qdrant to become available...'
  sleep 1
done
>&2 echo 'Qdrant is available'

exec "$@"

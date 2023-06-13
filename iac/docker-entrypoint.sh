#!/bin/bash

# if any of the commands in your code fails for any reason, the entire script fails
set -o errexit
# fail exit if one of your pipe command fails
set -o pipefail
# exits if any of your variables is not set
set -o nounset

# This is the function that is run in a loop until to check if the database is ready.
# It is used by the celery worker, flower and the web server containers.
postgres_ready() {
python << END
import sys

import psycopg2
import urllib.parse as urlparse
import os

url = urlparse.urlparse(os.environ['POSTGRES_URL'])
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port

try:
    psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)

END
}
until postgres_ready; do
  >&2 echo 'Waiting for PostgreSQL to become available...'
  sleep 1
done
>&2 echo 'PostgreSQL is available'

# make the entrypoint a pass through to ensure
# Docker runs the command the user passes
# in (e.g. `command: /start`)
exec "$@"

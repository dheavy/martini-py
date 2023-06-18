#!/bin/bash
set -a
source ../.env
set +a

# Define colors
RED='\033[0;31m'
NC='\033[0m' # No Color

# Set some env vars to localhost to override the value in .env
# currently set to the name of their container by Docker.
# This is because Docker will read the value from .env and use it,
# and we want to use localhost instead for local development.
POSTGRES_HOST=localhost
QDRANT_URL=http://localhost:6333
CELERY_BROKER_URL=redis://localhost:32787/0
CELERY_RESULT_BACKEND=redis://localhost:32787/0

# Run Django manage.py commands. Example: ./manage.sh makemigrations.
# Note: "$@" passes all arguments to the script.
python manage.py "$@"

# If the previous command failed, check if the error message contains "No such file or directory".
# If it does, then the user is not in the correct directory - hint at that.
if [ $? -ne 0 ]; then
    err=$(python manage.py "$@" 2>&1 >/dev/null)
    if [[ $err == *"No such file or directory"* ]]
    then
        echo -e "${RED}Could not find manage.py. Are you in the correct directory?${NC}"
    fi
fi

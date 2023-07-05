#!/bin/bash
set -a
source ../.env
set +a

# Define colors
RED='\033[0;31m'
NC='\033[0m' # No Color

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

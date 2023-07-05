#!/bin/bash

images=(
    "martini_flower"
    "martini-web_nginx"
    "martini_worker"
    "martini_beat"
    "martini_web"
)

echo "Removing uploads from shared volume..."
poetry run manage clear_static

echo "Resetting Docker containers, volumes and images..."
docker compose -f ../docker-compose.prod.yml down --volumes --remove-orphans
for img in "${images[@]}"; do
    docker rmi -f $img
done

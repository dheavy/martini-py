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
docker compose -f ../docker-compose.dev.yml down --volumes --remove-orphans
for img in "${images[@]}"; do
    docker rmi -f $img
done

echo "Rebuilding images and starting containers and volumes..."
docker compose -f ../docker-compose.dev.yml up --build -d && docker compose -f ../docker-compose.dev.yml logs -f

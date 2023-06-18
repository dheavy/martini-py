#!/bin/bash

images=(
    "martini_flower"
    "martini-web_nginx"
    "martini_worker"
    "martini_beat"
    "martini_web"
)

docker compose down --volumes
for img in "${images[@]}"; do
    docker rmi $img
done
docker compose up --build -d && docker compose logs -f

#!/bin/bash

echo "Shutting down Docker containers"
docker compose -f ../docker-compose.dev.yml down

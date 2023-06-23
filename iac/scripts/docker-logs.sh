#!/bin/bash

echo "Starting logs for all Docker containers..."
docker compose -f ../docker-compose.dev.yml logs -f

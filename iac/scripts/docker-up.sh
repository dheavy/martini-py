#!/bin/bash

echo "Rebuilding and starting services..."
docker compose -f ../docker-compose.dev.yml up --build -d

#!/bin/bash

echo "Shutting down Docker containers and volumes..."
docker compose down --volumes

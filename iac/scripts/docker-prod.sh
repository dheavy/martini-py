echo "Building production images and containers..."
docker compose -f ../docker-compose.prod.yml up --build -d && docker compose -f ../docker-compose.prod.yml logs -f

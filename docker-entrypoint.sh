#!/usr/bin/env bash
set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🚀 Starting RetroNetwork...${NC}"

echo -e "${YELLOW}⏳ Waiting for PostgreSQL...${NC}"
until pg_isready -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" -U "${DB_USER:-postgres}" > /dev/null 2>&1; do
  echo "  PostgreSQL is unavailable - sleeping..."
  sleep 2
done
echo -e "${GREEN}✅ PostgreSQL is ready${NC}"

echo -e "${YELLOW}⏳ Waiting for Redis...${NC}"
until redis-cli -h "${REDIS_HOST:-redis}" -p "${REDIS_PORT:-6379}" ping > /dev/null 2>&1; do
  echo "  Redis is unavailable - sleeping..."
  sleep 2
done
echo -e "${GREEN}✅ Redis is ready${NC}"

echo -e "${YELLOW}🔄 Running database migrations...${NC}"
if python manage.py migrate --noinput; then
  echo -e "${GREEN}✅ Migrations completed${NC}"
else
  echo -e "${RED}❌ Migrations failed${NC}"
  exit 1
fi

echo -e "${YELLOW}🔄 Collecting static files...${NC}"
if python manage.py collectstatic --noinput --clear > /dev/null 2>&1; then
  echo -e "${GREEN}✅ Static files collected${NC}"
else
  echo -e "${RED}⚠️  Warning: Static files collection had issues${NC}"
fi

mkdir -p /app/logs /app/staticfiles /app/media
echo -e "${GREEN}✅ Log directory ready${NC}"

echo -e "${YELLOW}🚀 Starting application with Daphne...${NC}"
echo -e "${GREEN}Application is ready to accept connections${NC}"
exec daphne -b 0.0.0.0 -p 8000 social_core.asgi:application


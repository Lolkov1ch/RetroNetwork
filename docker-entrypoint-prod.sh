#!/bin/bash
set -e

echo "=== Django Production Deployment ==="

# Verify DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL environment variable is not set"
    echo "Set DATABASE_URL to your managed PostgreSQL connection string"
    exit 1
fi

echo "✅ DATABASE_URL is configured"

# Retry logic for database migrations
MAX_RETRIES=5
RETRY_DELAY=3
ATTEMPT=1

while [ $ATTEMPT -le $MAX_RETRIES ]; do
    echo ""
    echo "Migration attempt $ATTEMPT/$MAX_RETRIES"
    if python manage.py migrate --noinput --verbosity 2; then
        echo "✅ Migrations completed successfully"
        break
    else
        if [ $ATTEMPT -lt $MAX_RETRIES ]; then
            echo "⚠️  Migration failed, waiting $RETRY_DELAY seconds before retry..."
            sleep $RETRY_DELAY
        else
            echo "❌ Migrations failed after $MAX_RETRIES attempts"
            exit 1
        fi
    fi
    ATTEMPT=$((ATTEMPT + 1))
done

echo ""
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear --verbosity 1

echo ""
echo "=== Starting Gunicorn ==="
exec gunicorn social_core.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers ${WEB_CONCURRENCY:-2} \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
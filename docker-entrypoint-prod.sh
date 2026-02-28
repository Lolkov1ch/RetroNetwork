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

MAX_RETRIES=5
RETRY_DELAY=3

run_step () {
    local label="$1"
    shift
    local attempt=1

    while [ $attempt -le $MAX_RETRIES ]; do
        echo ""
        echo "$label — attempt $attempt/$MAX_RETRIES"
        if python manage.py "$@"; then
            echo "✅ $label succeeded"
            return 0
        fi

        if [ $attempt -lt $MAX_RETRIES ]; then
            echo "⚠️  $label failed, waiting $RETRY_DELAY seconds before retry..."
            sleep $RETRY_DELAY
        else
            echo "❌ $label failed after $MAX_RETRIES attempts"
            return 1
        fi

        attempt=$((attempt + 1))
    done
}

# Users first (note: use -v 2)
run_step "Users migrations" migrate users --noinput -v 2

# Then everything else
run_step "All migrations" migrate --noinput -v 2

echo ""
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear -v 1

echo ""
echo "=== Starting Gunicorn ==="
exec gunicorn social_core.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers ${WEB_CONCURRENCY:-2} \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
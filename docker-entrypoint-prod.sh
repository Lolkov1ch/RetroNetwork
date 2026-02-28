#!/bin/bash
set -e

echo "=== Django Production Deployment ==="
echo "Environment: RENDER=${RENDER:-false}"
echo "DATABASE_URL is set: $([ -n "$DATABASE_URL" ] && echo "YES" || echo "NO")"

# Wait for database to be available with retries
if [ "$RENDER" = "true" ]; then
    echo "Detected Render environment - waiting for PostgreSQL..."
    sleep 15  # Give Render services time to initialize
fi

# Run migrations with automatic retries
echo "Running Django database migrations..."
max_migrations_retries=5
migration_attempt=0

while [ $migration_attempt -lt $max_migrations_retries ]; do
    echo "Migration attempt $((migration_attempt + 1))/$max_migrations_retries"
    if python manage.py migrate --noinput --verbosity 2; then
        echo "✓ Migrations completed successfully"
        break
    else
        migration_attempt=$((migration_attempt + 1))
        if [ $migration_attempt -lt $max_migrations_retries ]; then
            echo "Migration failed, waiting 5 seconds before retry..."
            sleep 5
        else
            echo "ERROR: Migrations failed after $max_migrations_retries attempts"
            exit 1
        fi
    fi
done

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear --verbosity 1

echo "✓ Deployment initialization complete"
echo "Starting Gunicorn server on 0.0.0.0:8000"
exec gunicorn social_core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

#!/bin/bash
set -e

echo "=== Django Production Deployment ==="
echo "RENDER environment: ${RENDER:-false}"

if [ "$RENDER" = "true" ]; then
    echo "Waiting for PostgreSQL to initialize..."
    
    # Use pg_isready if available, otherwise use psql
    if command -v pg_isready &> /dev/null; then
        echo "Using pg_isready to check database..."
        max_attempts=120
        attempt=0
        while [ $attempt -lt $max_attempts ]; do
            if pg_isready -h localhost -p 5432 -U postgres 2>/dev/null; then
                echo "✓ PostgreSQL is ready!"
                break
            fi
            attempt=$((attempt + 1))
            if [ $((attempt % 20)) -eq 0 ]; then
                echo "Still waiting for PostgreSQL ($attempt/$max_attempts)..."
            fi
            sleep 1
        done
    else
        echo "pg_isready not available, using basic wait..."
        sleep 30
    fi
fi

echo "Attempting to create database tables..."
max_migrations_retries=10
migration_attempt=0

while [ $migration_attempt -lt $max_migrations_retries ]; do
    migration_attempt=$((migration_attempt + 1))
    echo "Migration attempt $migration_attempt/$max_migrations_retries"
    
    if python manage.py migrate --noinput --verbosity 2; then
        echo "✓ Migrations completed successfully"
        break
    else
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
echo "Starting Gunicorn server..."
exec gunicorn social_core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

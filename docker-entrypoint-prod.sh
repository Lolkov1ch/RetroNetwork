#!/bin/bash
set -e

echo "=== Django Production Deployment ==="

# PostgreSQL password
PGPASSWORD="${POSTGRES_PASSWORD:-retronetwork_db_password}"
export PGPASSWORD

# Start PostgreSQL server in the background
echo "Starting PostgreSQL server..."
/etc/init.d/postgresql start || true

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
max_attempts=60
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if pg_isready -h localhost -U postgres >/dev/null 2>&1; then
        echo "✓ PostgreSQL is ready!"
        break
    fi
    attempt=$((attempt + 1))
    if [ $((attempt % 10)) -eq 0 ]; then
        echo "Still waiting for PostgreSQL ($attempt/$max_attempts)..."
    fi
    sleep 1
done

if [ $attempt -eq $max_attempts ]; then
    echo "PostgreSQL startup timeout, but continuing..."
fi

# Set password for postgres user if not already set
echo "Setting PostgreSQL postgres user password..."
psql -h localhost -U postgres -tc "ALTER USER postgres WITH PASSWORD '$PGPASSWORD';" 2>/dev/null || true

# Create django database if it doesn't exist
echo "Ensuring 'django' database exists..."
psql -h localhost -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'django'" 2>/dev/null | grep -q 1 || \
psql -h localhost -U postgres -c "CREATE DATABASE django" 2>/dev/null || true

# Run migrations
echo "Running Django database migrations..."
max_migrations_retries=5
migration_attempt=0

while [ $migration_attempt -lt $max_migrations_retries ]; do
    migration_attempt=$((migration_attempt + 1))
    echo "Migration attempt $migration_attempt/$max_migrations_retries"
    
    if python manage.py migrate --noinput --verbosity 2; then
        echo "✓ Migrations completed successfully"
        break
    else
        if [ $migration_attempt -lt $max_migrations_retries ]; then
            echo "Migration failed, waiting 3 seconds before retry..."
            sleep 3
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

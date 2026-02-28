#!/usr/bin/env bash
set -e

echo "Starting production deployment..."
echo "DATABASE_URL: ${DATABASE_URL:0:20}..." 

# If DATABASE_URL is set, wait for the database
if [ -n "$DATABASE_URL" ]; then
    echo "Waiting for PostgreSQL to be available..."
    max_retries=30
    retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        python << 'EOF'
import os
import psycopg2
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    conn.close()
    print('✓ Database ready!')
    exit(0)
except Exception as e:
    print(f'✗ Connection failed: {str(e)[:80]}')
    exit(1)
EOF
        if [ $? -eq 0 ]; then
            break
        fi
        retry_count=$((retry_count + 1))
        echo "Attempt $retry_count/$max_retries..."
        sleep 2
    done
    
    if [ $retry_count -eq $max_retries ]; then
        echo "ERROR: Could not connect to database after $max_retries attempts"
        exit 1
    fi
else
    echo "ERROR: DATABASE_URL environment variable is not set!"
    echo "Available environment variables:"
    env | grep -E "^[A-Z]" || true
    exit 1
fi

echo "Running Django database migrations..."
python manage.py migrate --noinput --verbosity 2

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear --verbosity 1

echo "✓ Initialization complete, starting Gunicorn..."
exec gunicorn social_core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

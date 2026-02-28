#!/usr/bin/env bash
set -e

echo "Starting production deployment..."

# Check if running on Render
if [ "$RENDER" = "true" ]; then
    echo "Detected Render environment"
    echo "Waiting for PostgreSQL service to be available..."
    
    # Render uses internal service names for service-to-service communication
    max_retries=60
    retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        python << 'EOF'
import os
import time
import socket

# Try to connect to the database service via Render's internal hostname
host = 'retronetwork-db'
port = 5432
timeout = 5

try:
    socket.create_connection((host, port), timeout=timeout)
    print(f'✓ PostgreSQL service available at {host}:{port}')
    exit(0)
except (socket.timeout, ConnectionRefusedError, OSError) as e:
    print(f'✗ Cannot reach {host}:{port} - {str(e)[:60]}')
    exit(1)
EOF
        if [ $? -eq 0 ]; then
            echo "✓ Database service is ready!"
            break
        fi
        retry_count=$((retry_count + 1))
        if [ $((retry_count % 10)) -eq 0 ]; then
            echo "Still waiting for database... (attempt $retry_count/$max_retries)"
        fi
        sleep 1
    done
    
    if [ $retry_count -eq $max_retries ]; then
        echo "ERROR: PostgreSQL service did not become available after $max_retries attempts"
        exit 1
    fi
else
    echo "Local development mode detected"
fi

echo "Running Django database migrations..."
python manage.py migrate --noinput --verbosity 2

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear --verbosity 1

echo "✓ Deployment initialization complete"
echo "Starting Gunicorn server on port 8000..."
exec gunicorn social_core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

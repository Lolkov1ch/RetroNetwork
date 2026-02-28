#!/usr/bin/env bash
set -e

echo "Starting production deployment..."
echo "Environment: RENDER=$RENDER"

# Give the database a moment to start (basic delay for Render's initialization)
if [ "$RENDER" = "true" ]; then
    echo "Waiting for services to initialize..."
    sleep 10
fi

echo "Running Django database migrations..."
# Migrations will retry connections automatically
python manage.py migrate --noinput --verbosity 2 || {
    echo "WARNING: Initial migration attempt failed, retrying..."
    sleep 5
    python manage.py migrate --noinput --verbosity 2
}

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

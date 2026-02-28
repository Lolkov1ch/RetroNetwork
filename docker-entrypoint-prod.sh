#!/usr/bin/env bash
set -e

echo "Starting production deployment..."
echo "DATABASE_URL is set: $( [ -z "$DATABASE_URL" ] && echo "NO" || echo "YES" )"

# Wait for database to be available (if using PostgreSQL)
if [ -n "$DATABASE_URL" ]; then
    echo "Waiting for PostgreSQL database to be available..."
    python -c "
import os
import time
import sys

try:
    import psycopg2
except ImportError:
    print('psycopg2 not found, trying alternative method')
    import subprocess
    sys.exit(0)

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            print('WARNING: DATABASE_URL not set!')
            sys.exit(1)
        
        conn = psycopg2.connect(db_url, connect_timeout=5)
        conn.close()
        print('✓ Database connection successful!')
        sys.exit(0)
    except Exception as e:
        retry_count += 1
        print(f'✗ Database not ready ({retry_count}/{max_retries}): {str(e)[:100]}')
        if retry_count >= max_retries:
            print('ERROR: Database connection failed after max retries!')
            sys.exit(1)
        time.sleep(2)
"
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to connect to database"
        exit 1
    fi
else
    echo "WARNING: DATABASE_URL not set, using fallback database configuration"
fi

echo "Checking Django database configuration..."
python -c "
from django.conf import settings
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_core.settings')
django.setup()
db_config = settings.DATABASES['default']
print(f'Database Engine: {db_config.get(\"ENGINE\", \"unknown\")}')
print(f'Database Name: {db_config.get(\"NAME\", \"unknown\")}')
"

echo "Running database migrations..."
python manage.py migrate --noinput --verbosity=2 || {
    echo "ERROR: Migration failed!"
    exit 1
}

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear --verbosity=2

echo "✓ Production deployment initialization complete"
echo "Starting Gunicorn server..."
exec gunicorn social_core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

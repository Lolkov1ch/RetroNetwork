#!/usr/bin/env bash
set -e

echo "Starting production deployment..."

# Wait for database to be available (if using PostgreSQL)
if [ -n "$DATABASE_URL" ]; then
    echo "Waiting for PostgreSQL database to be available..."
    python -c "
import os
import psycopg2
import time

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        # Parse DATABASE_URL to get connection params
        db_url = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(db_url)
        conn.close()
        print('Database is ready!')
        break
    except (psycopg2.OperationalError, psycopg2.DatabaseError) as e:
        retry_count += 1
        print(f'Database not ready yet. Attempt {retry_count}/{max_retries}')
        if retry_count >= max_retries:
            print('Database connection failed after max retries!')
            raise
        time.sleep(2)
"
fi

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Starting Gunicorn server..."
exec gunicorn social_core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

#!/bin/bash
set -e

echo "=== Django Production Deployment ==="
echo "DATABASE_URL is ${DATABASE_URL:+set}"

python manage.py migrate --noinput --verbosity 2
python manage.py collectstatic --noinput --clear --verbosity 1

exec gunicorn social_core.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers ${WEB_CONCURRENCY:-2} \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
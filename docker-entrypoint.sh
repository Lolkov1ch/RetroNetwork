#!/usr/bin/env bash
set -e

# Wait for database to be ready
while ! nc -z db 5432; do
  sleep 1
done

python manage.py migrate --noinput

# python manage.py collectstatic --noinput

python manage.py runserver 0.0.0.0:8000


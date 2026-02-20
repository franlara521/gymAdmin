#!/bin/sh
set -e

echo "==> Aplicando migraciones..."
.venv/bin/python manage.py migrate --noinput

echo "==> Iniciando gunicorn..."
exec .venv/bin/gunicorn gym.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -

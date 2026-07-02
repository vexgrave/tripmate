#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# На бесплатном тарифе Render нет доступа к Shell/One-Off Jobs, поэтому
# суперпользователь и тестовые данные создаются прямо при сборке.
# Переменные DJANGO_SUPERUSER_* задаются в Render → Environment.
if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
  python manage.py createsuperuser --noinput || true
fi
python manage.py seed_data

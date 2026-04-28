#!/bin/sh
set -e

echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
# -q for "quiet" (no output except errors)
# Loop runs as long as pg_isready does NOT succeed (exit code != 0)
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -q; do
  echo "PostgreSQL is not ready - sleeping 1 second"
  sleep 1
done

echo "PostgreSQL is ready - continuing..."

# Run Django management commands
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate

# Create a superuser using environment variables
python manage.py shell <<EOF
import os
from django.contrib.auth import get_user_model
User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'adminpassword')

if not User.objects.filter(email=email).exists():
    print(f"Creating superuser '{username}'...")
    User.objects.create_superuser(email=email, password=password)
    print(f"Superuser '{username}' created.")
else:
    print(f"Superuser '{username}' already exists.")
EOF

python manage.py rqworker emails videos default &
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --reload

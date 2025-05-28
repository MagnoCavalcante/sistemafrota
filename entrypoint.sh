#!/bin/bash

# Espera o banco de dados estar pronto
echo "Waiting for database..."
while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
  sleep 0.1
done
echo "Database is up!"

# Aplica as migrações
python manage.py migrate

# Inicia o Gunicorn
exec gunicorn sistemafrota.wsgi:application \
    --bind 0.0.0.0:${PORT:-10000} \
    --workers ${WEB_CONCURRENCY:-4} \
    --log-level=info \
    --access-logfile=- \
    --error-logfile=- 
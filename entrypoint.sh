#!/bin/bash

# Extrai host e porta do DATABASE_URL se DATABASE_HOST não estiver definido
if [ -z "$DATABASE_HOST" ] && [ ! -z "$DATABASE_URL" ]; then
    # Exemplo de DATABASE_URL: postgres://user:pass@host:5432/dbname
    DATABASE_HOST=$(echo $DATABASE_URL | awk -F[@/] '{print $4}' | cut -d':' -f1)
    DATABASE_PORT=$(echo $DATABASE_URL | awk -F[@/:] '{print $5}')
fi

# Define valores padrão se ainda não estiverem definidos
DATABASE_HOST=${DATABASE_HOST:-localhost}
DATABASE_PORT=${DATABASE_PORT:-5432}

echo "Waiting for database at $DATABASE_HOST:$DATABASE_PORT..."

# Tenta conectar ao banco de dados
for i in {1..30}; do
    if nc -z $DATABASE_HOST $DATABASE_PORT; then
        echo "Database is up!"
        break
    fi
    echo "Waiting for database... ($i/30)"
    sleep 2
done

# Aplica as migrações
echo "Running migrations..."
python manage.py migrate --noinput

# Coleta arquivos estáticos
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Inicia o Gunicorn
echo "Starting Gunicorn..."
exec gunicorn sistemafrota.wsgi:application \
    --bind 0.0.0.0:${PORT:-10000} \
    --workers ${WEB_CONCURRENCY:-4} \
    --log-level=debug \
    --access-logfile=- \
    --error-logfile=- \
    --timeout 120 
#!/bin/bash
set -e

# Função para log
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S %Z')] $@"
}

# Extrai host e porta do DATABASE_URL se DATABASE_HOST não estiver definido
if [ -z "$DATABASE_HOST" ] && [ ! -z "$DATABASE_URL" ]; then
    # Exemplo de DATABASE_URL: postgres://user:pass@host:5432/dbname
    DATABASE_HOST=$(echo $DATABASE_URL | awk -F[@/] '{print $4}' | cut -d':' -f1)
    DATABASE_PORT=$(echo $DATABASE_URL | awk -F[@/:] '{print $5}')
fi

# Define valores padrão se ainda não estiverem definidos
DATABASE_HOST=${DATABASE_HOST:-localhost}
DATABASE_PORT=${DATABASE_PORT:-5432}

log "Waiting for database at $DATABASE_HOST:$DATABASE_PORT..."

# Tenta conectar ao banco de dados
max_tries=30
count=0
while [ $count -lt $max_tries ]; do
    if nc -z $DATABASE_HOST $DATABASE_PORT; then
        log "Database is up!"
        break
    fi
    count=$((count + 1))
    log "Waiting for database... ($count/$max_tries)"
    sleep 2
done

if [ $count -eq $max_tries ]; then
    log "Error: Could not connect to database after $max_tries attempts"
    exit 1
fi

# Aplica as migrações
log "Running migrations..."
python manage.py migrate --noinput || {
    log "Error: Failed to apply migrations"
    exit 1
}

# Coleta arquivos estáticos
log "Collecting static files..."
python manage.py collectstatic --noinput || {
    log "Error: Failed to collect static files"
    exit 1
}

# Configura o Gunicorn
GUNICORN_WORKERS=${WEB_CONCURRENCY:-4}
GUNICORN_THREADS=${GUNICORN_THREADS:-3}
GUNICORN_TIMEOUT=${GUNICORN_TIMEOUT:-120}
GUNICORN_MAX_REQUESTS=${GUNICORN_MAX_REQUESTS:-1000}
GUNICORN_MAX_REQUESTS_JITTER=${GUNICORN_MAX_REQUESTS_JITTER:-50}

log "Starting Gunicorn with $GUNICORN_WORKERS workers..."
exec gunicorn sistemafrota.wsgi:application \
    --bind 0.0.0.0:${PORT:-10000} \
    --workers $GUNICORN_WORKERS \
    --threads $GUNICORN_THREADS \
    --worker-class=gthread \
    --worker-tmp-dir=/dev/shm \
    --log-level=info \
    --access-logfile=- \
    --error-logfile=- \
    --timeout $GUNICORN_TIMEOUT \
    --max-requests $GUNICORN_MAX_REQUESTS \
    --max-requests-jitter $GUNICORN_MAX_REQUESTS_JITTER \
    --capture-output \
    --enable-stdio-inheritance 
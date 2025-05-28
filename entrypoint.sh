#!/bin/bash
set -e

# Função para log
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S %Z')] $@"
}

# Verifica se DATABASE_URL está definido
if [ -z "$DATABASE_URL" ]; then
    log "ERROR: DATABASE_URL is not set"
    exit 1
fi

# Função para extrair informações do DATABASE_URL
parse_db_url() {
    if [ ! -z "$DATABASE_URL" ]; then
        log "Parsing DATABASE_URL..."
        
        local tmp_url=${DATABASE_URL#*://}
        local userpass=${tmp_url%%@*}
        local hostportdb=${tmp_url#*@}
        local hostport=${hostportdb%/*}
        DATABASE_HOST=${hostport%:*}
        DATABASE_PORT=${hostport#*:}
        DATABASE_NAME=${hostportdb#*/}

        DATABASE_USER=${userpass%%:*}
        DATABASE_PASSWORD=${userpass#*:}

        log "Successfully parsed DATABASE_URL"
        log "Host: $DATABASE_HOST"
        log "Port: $DATABASE_PORT"
        log "Database: $DATABASE_NAME"
        log "User: $DATABASE_USER"
    else
        log "ERROR: DATABASE_URL is empty"
        exit 1
    fi
}

# Extrai informações do banco de dados
parse_db_url

# Define valores padrão se ainda não estiverem definidos
DATABASE_HOST=${DATABASE_HOST:-localhost}
DATABASE_PORT=${DATABASE_PORT:-5432}

log "Attempting to connect to database at $DATABASE_HOST:$DATABASE_PORT..."

# Tenta conectar ao banco de dados com timeout maior
max_tries=60  # 60 tentativas = 5 minutos
count=0
while [ $count -lt $max_tries ]; do
    if PGPASSWORD=$DATABASE_PASSWORD psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -c '\q' 2>/dev/null; then
        log "Successfully connected to database!"
        break
    fi
    count=$((count + 1))
    log "Waiting for database... ($count/$max_tries) - Host: $DATABASE_HOST, Port: $DATABASE_PORT"
    sleep 5  # 5 segundos entre tentativas
done

if [ $count -eq $max_tries ]; then
    log "ERROR: Could not connect to database after $max_tries attempts"
    log "Database connection details:"
    log "Host: $DATABASE_HOST"
    log "Port: $DATABASE_PORT"
    log "Database: $DATABASE_NAME"
    log "User: $DATABASE_USER"
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
GUNICORN_WORKERS=${WEB_CONCURRENCY:-2}
GUNICORN_THREADS=${GUNICORN_THREADS:-4}
GUNICORN_TIMEOUT=${GUNICORN_TIMEOUT:-180}
GUNICORN_MAX_REQUESTS=${GUNICORN_MAX_REQUESTS:-1000}
GUNICORN_MAX_REQUESTS_JITTER=${GUNICORN_MAX_REQUESTS_JITTER:-50}
GUNICORN_KEEPALIVE=${GUNICORN_KEEPALIVE:-65}

log "Starting Gunicorn with $GUNICORN_WORKERS workers and $GUNICORN_THREADS threads..."
exec gunicorn sistemafrota.wsgi:application \
    --bind 0.0.0.0:${PORT:-10000} \
    --workers $GUNICORN_WORKERS \
    --threads $GUNICORN_THREADS \
    --worker-class=gthread \
    --worker-tmp-dir=/dev/shm \
    --log-level=debug \
    --access-logfile=- \
    --error-logfile=- \
    --timeout $GUNICORN_TIMEOUT \
    --keep-alive $GUNICORN_KEEPALIVE \
    --max-requests $GUNICORN_MAX_REQUESTS \
    --max-requests-jitter $GUNICORN_MAX_REQUESTS_JITTER \
    --capture-output \
    --enable-stdio-inheritance \
    --graceful-timeout 180 \
    --preload 
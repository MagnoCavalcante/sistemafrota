#!/bin/bash
set -e

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S %Z')] $@"
}

# Verifica se DATABASE_URL está definida
if [ -z "$DATABASE_URL" ]; then
    log "ERROR: DATABASE_URL is not set"
    exit 1
fi

# Função para extrair informações da DATABASE_URL
parse_db_url() {
    log "Parsing DATABASE_URL..."

    local tmp_url=${DATABASE_URL#*://}
    local userpass=${tmp_url%%@*}
    local hostportdb=${tmp_url#*@}
    local hostport=${hostportdb%/*}
    DATABASE_NAME=${hostportdb#*/}

    # Extrai usuário e senha
    DATABASE_USER=${userpass%%:*}
    DATABASE_PASSWORD=${userpass#*:}

    # Extrai host e porta
    if [[ "$hostport" == *:* ]]; then
        DATABASE_HOST=${hostport%:*}
        DATABASE_PORT=${hostport#*:}
    else
        DATABASE_HOST=$hostport
        DATABASE_PORT=5432
    fi

    log "Successfully parsed DATABASE_URL"
    log "Host: $DATABASE_HOST"
    log "Port: $DATABASE_PORT"
    log "Database: $DATABASE_NAME"
    log "User: $DATABASE_USER"
}

parse_db_url

log "Attempting to connect to database at $DATABASE_HOST:$DATABASE_PORT..."

PGPASSWORD=$DATABASE_PASSWORD psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -c '\q' 2>/dev/null && {
    log "Successfully connected to database!"
} || {
    log "WARNING: Could not connect to database on first attempt. Proceeding anyway..."
}

log "Running migrations..."
python manage.py migrate --noinput || {
    log "Error: Failed to apply migrations"
    exit 1
}

log "Collecting static files..."
python manage.py collectstatic --noinput || {
    log "Error: Failed to collect static files"
    exit 1
}

# Configura Gunicorn
GUNICORN_WORKERS=${WEB_CONCURRENCY:-2}
GUNICORN_THREADS=${GUNICORN_THREADS:-4}
GUNICORN_TIMEOUT=${GUNICORN_TIMEOUT:-180}
GUNICORN_MAX_REQUESTS=${GUNICORN_MAX_REQUESTS:-1000}
GUNICORN_MAX_REQUESTS_JITTER=${GUNICORN_MAX_REQUESTS_JITTER:-50}
GUNICORN_KEEPALIVE=${GUNICORN_KEEPALIVE:-65}

log "Starting Gunicorn with $GUNICORN_WORKERS workers and $GUNICORN_THREADS threads..."

gunicorn sistemafrota.wsgi:application \
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
    --preload || {
        log "ERROR: Gunicorn failed to start"
        exit 1
    }

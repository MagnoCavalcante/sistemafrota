#!/bin/bash

set -e

# Função para aguardar o PostgreSQL
wait_for_postgres() {
    echo "Aguardando o PostgreSQL..."
    while ! pg_isready -h db -U $POSTGRES_USER -d $POSTGRES_DB; do
        sleep 1
    done
    echo "PostgreSQL está pronto e em execução!"
}

# Aguardar PostgreSQL
wait_for_postgres

# Criar banco de dados e usuário se não existirem
echo "Configurando banco de dados..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -c "CREATE DATABASE $POSTGRES_DB;" || true
PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -c "CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';" || true
PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -c "ALTER USER $POSTGRES_USER WITH SUPERUSER;" || true
PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -c "GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;" || true

# Aplicar migrações do banco de dados
echo "Aplicando migrações do banco de dados..."
python manage.py migrate

# Iniciar Gunicorn
echo "Iniciando o Gunicorn..."
exec /opt/venv/bin/gunicorn sistemafrota.wsgi:application --bind 0.0.0.0:8000 --workers 3 
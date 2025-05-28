FROM python:3.11-slim

WORKDIR /app

# Instala as dependências necessárias
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos do projeto
COPY . .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Coleta arquivos estáticos
RUN python manage.py collectstatic --noinput

# Expõe a porta que o gunicorn vai usar
EXPOSE ${PORT:-8000}

# Comando para iniciar o servidor
CMD gunicorn sistemafrota.wsgi:application --bind 0.0.0.0:${PORT:-8000} 
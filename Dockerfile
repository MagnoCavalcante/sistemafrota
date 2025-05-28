FROM python:3.11-slim

WORKDIR /app

# Configuração do ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Instala as dependências necessárias
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos do projeto
COPY . .

# Garante que o script de entrypoint tem permissões de execução
RUN chmod +x entrypoint.sh

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Cria diretórios necessários e ajusta permissões
RUN mkdir -p /app/staticfiles /app/media && \
    chmod -R 755 /app/staticfiles /app/media

# Coleta arquivos estáticos
RUN python manage.py collectstatic --noinput

# Expõe a porta que o gunicorn vai usar
EXPOSE ${PORT:-10000}

# Define o script de entrypoint
ENTRYPOINT ["/app/entrypoint.sh"] 
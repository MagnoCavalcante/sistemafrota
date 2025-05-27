FROM python:3.11-slim as builder

# Defina variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Instale as dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crie e ative o ambiente virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instale as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage final
FROM python:3.11-slim

# Copie o ambiente virtual do builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Crie um usuário não-root
RUN useradd -m -s /bin/bash app_user

# Instale apenas as dependências de runtime necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Configure o diretório de trabalho
WORKDIR /app

# Copie o projeto
COPY --chown=app_user:app_user . .

# Colete arquivos estáticos
RUN python manage.py collectstatic --noinput

# Configure as permissões
RUN chown -R app_user:app_user /app

# Mude para o usuário não-root
USER app_user

# Exponha a porta
EXPOSE 8000

# Configure o comando de entrada
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "sistemafrota.wsgi:application"] 
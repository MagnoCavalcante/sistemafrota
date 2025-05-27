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
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crie e ative o ambiente virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copie apenas os arquivos de dependências primeiro
COPY requirements.txt .

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn==21.2.0

# Stage final
FROM python:3.11-slim

# Copie o ambiente virtual do builder
COPY --from=builder /opt/venv /opt/venv

# Configure o PATH para incluir o ambiente virtual
ENV PATH="/opt/venv/bin:$PATH" \
    VIRTUAL_ENV="/opt/venv" \
    PYTHONPATH="/app"

# Crie um usuário não-root
RUN useradd -m -s /bin/bash app_user

# Instale apenas as dependências de runtime necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Configure o diretório de trabalho
WORKDIR /app

# Copie o entrypoint primeiro e configure suas permissões
COPY --chown=app_user:app_user entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Copie o resto do projeto
COPY --chown=app_user:app_user . .

# Verifique se o gunicorn está instalado e acessível
RUN /opt/venv/bin/gunicorn --version

# Mude para o usuário não-root
USER app_user

# Exponha a porta
EXPOSE 8000

# Use o script de entrada como ponto de entrada
ENTRYPOINT ["/app/entrypoint.sh"] 
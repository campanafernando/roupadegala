FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/opt/venv/bin:$PATH"

# Instala dependências do sistema (removidas dependências desnecessárias para API)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    python3-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Diretório da aplicação
WORKDIR /app

# Copia o requirements
COPY requirements.txt /app/requirements.txt

# Cria venv, ativa e instala tudo com uv
RUN python3 -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install uv \
    && uv pip install -r /app/requirements.txt

# Copia o código da aplicação
COPY . /app

# Comando padrão: migrate e inicia gunicorn para API REST
CMD ["sh", "-c", "python manage.py migrate && gunicorn roupadegala.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120"]

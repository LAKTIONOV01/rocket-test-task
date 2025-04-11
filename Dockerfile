FROM python:3.10-slim

# Установка зависимостей для PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt



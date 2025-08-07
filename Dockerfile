FROM ubuntu:latest
LABEL authors="Roman"

ENTRYPOINT ["top", "-b"]# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение
COPY . .

# Устанавливаем переменные окружения (можно переопределить в docker-compose)
ENV PYTHONPATH=/app

# Проверка, что приложение работает
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
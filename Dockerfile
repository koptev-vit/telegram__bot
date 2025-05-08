# Используем официальный Python-образ
FROM python:3.11-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /usr/src/app

# Копируем файлы проекта
COPY . .

# Установка зависимостей Python
RUN pip install --no-cache-dir -r requirements.txt

# Указание команды запуска
CMD ["python", "app/main.py"]

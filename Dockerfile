# Используем стабильную версию
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем только requirements.txt для кэширования слоев докера
COPY requirements.txt .

# Устанавливаем зависимости без кэша (чтобы образ был легче)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код
COPY . .

# Запускаем бота
CMD ["python", "bot.py"]
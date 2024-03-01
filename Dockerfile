FROM python:latest

# Установка рабочего каталога в контейнере
WORKDIR /telegram

# Копирование файлов проекта в контейнер
COPY . /telegram

# Установка зависимостей Python
RUN pip install --no-cache-dir -r requirements.txt

# Команда для запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

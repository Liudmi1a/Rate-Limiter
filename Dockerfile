FROM python:3.11-slim

#рабочая директория в контейнере
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#порт, который будет слушать приложение
EXPOSE 8000

#запуск приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
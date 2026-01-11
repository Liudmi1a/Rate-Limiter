# Rate Limiter API

REST API сервис для ограничения частоты запросов по алгоритму Fixed Window. Поддерживает глобальные лимиты и лимиты по IP-адресу клиента. 

### Запуск через Docker

### Требования
- [Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/install/)
- Git

### Шаги запуска
```bash
# 1. Клонировать репозиторий
git clone https://github.com/<Liudmi1a>/rate_limiter.git
cd rate_limiter

# 2. Настроить переменные окружения
cp .env.example .env
# Отредактировать .env при необходимости

# 3. Запустить систему командой
docker-compose up --build
```
### Запуск вручную без Docker
```bash
# 1. Клонировать репозиторий
git clone https://github.com/<Liudmi1a>/rate_limiter.git
cd rate_limiter

# 2. Создать виртуальное окружение
python -m venv venv

# 3. Активировать виртуальное окружение
venv\Scripts\activate

# 4. Установить зависимости
pip install -r requirements.txt

# 5. Настроить переменные окружения
cp .env.example .env

# 6. Запустить Redis в отдельном терминале
redis-server

# 7. Запустить приложение
uvicorn main:app --reload
```
### Структура проекта
```
rate_limiter/
├── main.py             
├── rate_limit.py        
├── storage.py       
├── requirements.txt  
├── Dockerfile   
├── docker-compose.yml 
├── .env.example 
├── .dockerignore  
└── .gitignore 

```

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from rate_limit import RateLimiter

app = FastAPI(
    title="Rate Limiter API", 
    description="Ограничитель трафика - защита API от перегрузки"
)

limiter = RateLimiter()

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
        return ip
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"

class CheckRequest(BaseModel):
    resource: str = "resource"

class CheckResponse(BaseModel):
    allowed: bool
    global_remaining: int
    ip_remaining: int
    global_limit: int
    ip_limit: int
    window_seconds: int
    message: str

class ConfigRequest(BaseModel):
    global_limit: int
    ip_limit: int
    window_seconds: int = 60

class CreateResourceRequest(BaseModel):
    name: str
    global_limit: int
    ip_limit: int
    window_seconds: int = 60

@app.get("/", summary="Главная страница", tags=["Общее"])
def read_root():
    return {"message": "Rate Limiter API работает"}

@app.post("/check", response_model=CheckResponse, 
          summary="Проверить лимит запросов", tags=["Основные"])
def check_rate_limit(request: CheckRequest, fastapi_request: Request):
    client_ip = get_client_ip(fastapi_request)
    allowed, info = limiter.check_request(request.resource, client_ip)
    message = "Запрос разрешен" if allowed else "Превышен лимит запросов"
    
    return CheckResponse(
        allowed=allowed,
        global_remaining=info['global_remaining'],
        ip_remaining=info['ip_remaining'],
        global_limit=info['global_limit'],
        ip_limit=info['ip_limit'],
        window_seconds=info['window_seconds'],
        message=message
    )

@app.post("/config", summary="Обновить конфигурацию", tags=["Администрирование"])
def update_config(request: ConfigRequest):
    limiter.update_config(
        resource="resource",
        global_limit=request.global_limit,
        ip_limit=request.ip_limit,
        window_seconds=request.window_seconds
    )
    return {"status": "успех", "message": "Конфигурация обновлена"}

@app.get("/status", summary="Статус сервиса", tags=["Администрирование"])
def get_status():
    return {
        "status": "активен",
        "redis_connected": limiter.storage.is_connected(),
        "default_limits": limiter.config['resource']
    }

@app.post("/resources", summary="Создать новый ресурс", tags=["Ресурсы"])
def create_resource(request: CreateResourceRequest):
    limiter.update_config(
        resource=request.name,
        global_limit=request.global_limit,
        ip_limit=request.ip_limit,
        window_seconds=request.window_seconds
    )
    return {"status": "успех", "message": f"Ресурс {request.name} создан"}

@app.delete("/resources/{resource_name}", summary="Удалить ресурс", tags=["Ресурсы"])
def delete_resource(resource_name: str):
    if resource_name in limiter.config:
        del limiter.config[resource_name]
        limiter.storage.save_config(limiter.config_key, limiter.config)
        return {"status": "успех", "message": f"Ресурс {resource_name} удален"}
    else:
        raise HTTPException(status_code=404, detail="Ресурс не найден")

@app.get("/resources", summary="Список ресурсов", tags=["Ресурсы"])
def list_resources():
    return {"resources": list(limiter.config.keys())}

@app.get("/resources/{resource_name}", summary="Конфигурация ресурса", tags=["Ресурсы"])
def get_resource_config(resource_name: str):
    """
    Получить конфигурацию для указанного ресурса
    """
    config = limiter.get_resource_config(resource_name)
    if not config:
        raise HTTPException(status_code=404, detail="Ресурс не найден")
    return config

@app.post("/reset", summary="Сбросить все счетчики", tags=["Администрирование"])
def reset_counters():
    """
    Сбросить ВСЕ счетчики запросов в системе
    """
    try:
        limiter.reset_counters()
        return {"status": "успех", "message": "Все счетчики сброшены"}
    except Exception as e:

        raise HTTPException(status_code=500, detail=f"Ошибка сброса: {str(e)}") 

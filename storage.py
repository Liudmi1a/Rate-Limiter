import redis
import json
import os
from dotenv import load_dotenv

#переменные из .env файла
load_dotenv()

class RedisStorage:
    
    def __init__(self):
        host = os.getenv("REDIS_HOST", "localhost")   #из .env или 'localhost'
        port = int(os.getenv("REDIS_PORT", 6379))     # <из .env или 6379
        
        self.redis = redis.Redis(
            host=host,         
            port=port,        
            decode_responses=True
        )
    
    def save_config(self, config_key: str, config_data: dict):
        self.redis.set(config_key, json.dumps(config_data))
    
    def load_config(self, config_key: str, default_config: dict) -> dict:
        config_json = self.redis.get(config_key)
        if config_json:
            return json.loads(config_json)
        else:
            self.save_config(config_key, default_config)
            return default_config
    
    def is_connected(self) -> bool:
        return self.redis.ping()
import redis
import json

class RedisStorage:
    def __init__(self):
        self.redis = redis.Redis(
            host='localhost', 
            port=6379, 
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
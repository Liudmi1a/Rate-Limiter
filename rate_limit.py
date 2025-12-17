from storage import RedisStorage
from typing import Dict, Tuple, Optional
import time

class RateLimiter:
    def __init__(self):
        self.storage = RedisStorage()
        self.config_key = "rate_limiter_config"
        default_config = {
            'resource': {
                'global_limit': 100,
                'ip_limit': 10,
                'window_seconds': 60
            }
        }
        self.config = self.storage.load_config(self.config_key, default_config)

    def check_request(self, resource: str, client_ip: str) -> Tuple[bool, Dict]:
        resource_config = self.config.get(resource)
        if not resource_config:
            resource_config = self.config.get('resource', {
                'global_limit': 100,
                'ip_limit': 10,
                'window_seconds': 60
            })
        global_limit = resource_config['global_limit']
        ip_limit = resource_config['ip_limit']
        window_seconds = resource_config['window_seconds']
        current_window = self._get_current_window(window_seconds)
        global_key = f"rate_limit:global:{resource}:{current_window}"
        ip_key = f"rate_limit:ip:{resource}:{client_ip}:{current_window}"
        ttl = window_seconds + 10
        lua_script = """
        local global_key = KEYS[1]
        local ip_key = KEYS[2]
        local global_limit = tonumber(ARGV[1])
        local ip_limit = tonumber(ARGV[2])
        local ttl = tonumber(ARGV[3])
        local global_current = tonumber(redis.call('GET', global_key) or 0)
        local ip_current = tonumber(redis.call('GET', ip_key) or 0)
        local allowed = 0
        if global_current < global_limit and ip_current < ip_limit then
            allowed = 1
            global_current = redis.call('INCR', global_key)
            ip_current = redis.call('INCR', ip_key)
            redis.call('EXPIRE', global_key, ttl)
            redis.call('EXPIRE', ip_key, ttl)
        end
        return {allowed, global_current, ip_current}
        """
        result = self.storage.redis.eval(
            lua_script,
            2,
            global_key,
            ip_key,
            global_limit,
            ip_limit,
            ttl
        )
        allowed = bool(result[0])
        global_current = int(result[1])
        ip_current = int(result[2])
        global_remaining = max(0, global_limit - global_current)
        ip_remaining = max(0, ip_limit - ip_current)
        return allowed, {
            'global_remaining': global_remaining,
            'ip_remaining': ip_remaining,
            'global_limit': global_limit,
            'ip_limit': ip_limit,
            'window_seconds': window_seconds
        }
           
    def update_config(self, resource: str, global_limit: int, ip_limit: int, window_seconds: int):
        self.config[resource] = {
            'global_limit': global_limit,
            'ip_limit': ip_limit,
            'window_seconds': window_seconds
        }
        self.storage.save_config(self.config_key, self.config)
    
    def get_resource_config(self, resource: str) -> Optional[Dict]:
        return self.config.get(resource)
    
    def get_all_resources(self) -> list:
        return list(self.config.keys())
    
    def reset_counters(self):
        keys = self.storage.redis.keys("rate_limit:*")
        if keys:
            self.storage.redis.delete(*keys)
    
    def _get_current_window(self, window_seconds: int) -> str:
        current_time = int(time.time())
        window_number = current_time // window_seconds
        return str(window_number)
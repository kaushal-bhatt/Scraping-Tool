import redis
from typing import Optional

class Cache:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.redis = redis.Redis(host=host, port=port, db=db)

    def get(self, key: str) -> Optional[str]:
        return self.redis.get(key)

    def set(self, key: str, value: str):
        self.redis.set(key, value)
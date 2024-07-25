import os

API_KEY = os.getenv("API_KEY", "your-secret-api-key")
REDIS_HOST = os.getenv("REDIS_HOST", "redis-cache")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
DATABASE_FILE = os.getenv("DATABASE_FILE", "products.json")
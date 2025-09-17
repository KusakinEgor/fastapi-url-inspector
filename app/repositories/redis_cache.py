import redis.asyncio as redis
from app.config import REDIS_URL

redis_client = redis.Redis(REDIS_URL, decode_responses=True)

async def set_value(key: str, value: str):
    await redis_client.set(key, value, ex=60)

async def get_value(key: str):
    await redis_client.get(key)

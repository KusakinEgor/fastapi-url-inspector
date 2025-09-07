import redis.asyncio as redis

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

async def set_value(key: str, value: str):
    await redis_client.set(key, value, ex=60)

async def get_value(key: str):
    await redis_client.get(key)

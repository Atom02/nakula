import aioredis
import json
from typing import Any
import os

redis_url = os.getenv("REDIS_URL", "redis://localhost")

class myCache():
    def __init__(self, redis_url: str = redis_url, ttl: int = 60*60*24):
        self.redis_url = redis_url
        self.ttl = ttl
        self.redis = aioredis.from_url(redis_url, decode_responses=True)

    async def __setitem__(self, key: str, value: Any):
        await self.redis.set(key, json.dumps(value), ex=self.ttl)

    async def __getitem__(self, key: str) -> Any:
        value = await self.redis.get(key)
        if value is not None:
            return json.loads(value)
        else:
            raise KeyError(f"Key {key} not found")

    async def __delitem__(self, key: str):
        await self.redis.delete(key)

    async def __contains__(self, key: str) -> bool:
        return await self.redis.exists(key) > 0

    def __repr__(self):
        return f'{self.__class__.__name__}(Redis: {self.redis_url})'
    
    async def has(self, key: str = None, ret: bool = False) -> bool:
        if key is None:
            raise ValueError("Specify a Key")
        return await self.__contains__(key)

    async def get(self, key: str = None, ret: Any = None) -> Any:
        if key is None:
            raise ValueError("Specify a Key")
        try:
            return await self.__getitem__(key)
        except KeyError:
            return ret
    
    async def set(self, key: str = None, val: Any = None) -> Any:
        if key is None or val is None:
            raise ValueError("Specify a Key and a value")
        await self.__setitem__(key, val)
        return await self.get(key)
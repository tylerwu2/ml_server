# implement redis cache to cache recent results 

import hashlib, json
import redis.asyncio as redis
from api.config import Settings

settings = Settings()

class PredictionCache():
    def __init__(self):
        self._client = None 

    async def connect(self):
        self._client = redis.from_url(settings.redis_url, decode_responses=True)

    async def close(self):
        if self._client:
            await self._client.aclose()

    async def ping(self):
        try:
            return await self._client.ping()
        except Exception:
            return False 
        
    def _key(self, text): 
        hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        return f"pred:{hash}" # print text-hash mapping
    
    async def get(self, text):
        raw = await self._client.get(self._key(text))
        return json.loads(raw) if raw else None 
    
    async def set(self, text, result, ttl=3600):
        await self._client.set(self._key(text), ttl, json.dumps(result))
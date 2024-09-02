from cachetools import TTLCache
from .rediscache import myCache
import os

usecache = os.getenv("CACHE","ttl")
if usecache == "ttl":
    cache = TTLCache(maxsize=500, ttl=60*60*24)
elif usecache == "redis":
    cache = myCache()
else:
    raise ValueError("No Cache Defined")
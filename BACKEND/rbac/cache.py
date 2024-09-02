from cachetools import TTLCache

class myCache():
    _cache = None
    def __init__(self):
        self._cache = TTLCache(maxsize=200, ttl=60*60*24)
    
    def __setitem__(self, key, value):
        self._cache[key] = value

    def __getitem__(self, key):
        return self._cache[key]

    def __delitem__(self, key):
        del self._cache[key]

    def __contains__(self, key):
        return key in self._cache

    def __repr__(self):
        return f'{self.__class__.__name__}({self._cache})'
    
    def has(self,key=None, ret=False):
        if key is None:
            raise ValueError("Specifiy a Key")
        
        if self._cache.get(key,None) != None:
            return True
        else:
            return ret
    
    def get(self,key=None, ret=None):
        if key is None:
            raise ValueError("Specifiy a Key")
        self._cache.get(key,ret)
    
    def set(self,key=None,val=None):
        if key is None or val is None:
            raise ValueError("Specifiy a Key and a value")
        try:
            self._cache[key] = val
            ret=self._cache.get(key)
        except Exception:
            ret=False
        return ret



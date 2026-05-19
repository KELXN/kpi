from functools import wraps
from collections import OrderedDict
import time
from typing import Callable, Any, Optional, Dict, Tuple
import hashlib


class Memoizer:
    def __init__(self, maxsize: Optional[int] = None, policy: str = "lru", ttl: Optional[float] = None):
        self.maxsize = maxsize
        self.policy = policy.lower()
        self.ttl = ttl
        self.cache: Dict[str, Tuple[Any, float, int]] = {}
        self.order = OrderedDict()

    def _make_key(self, args: tuple, kwargs: dict) -> str:
        key = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key.encode()).hexdigest()

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = self._make_key(args, kwargs)
            now = time.time()

            # Перевірка TTL
            if key in self.cache:
                result, timestamp, count = self.cache[key]
                if self.ttl and (now - timestamp > self.ttl):
                    self._evict(key)
                else:
                    self.cache[key] = (result, timestamp, count + 1)
                    if self.policy == "lru":
                        self.order.move_to_end(key)
                    return result

            # Обчислення
            result = func(*args, **kwargs)
            self.cache[key] = (result, now, 1)

            if self.policy == "lru":
                self.order[key] = None

            self._evict_if_needed()
            return result

        return wrapper

    def _evict_if_needed(self):
        if self.maxsize is None or len(self.cache) <= self.maxsize:
            return

        if self.policy == "lru":
            if self.order:
                oldest = next(iter(self.order))
                self._evict(oldest)
                self.order.popitem(last=False)

        elif self.policy == "lfu":
            if self.cache:
                min_count = min(c for _, _, c in self.cache.values())
                for k in list(self.cache.keys()):
                    if self.cache[k][2] == min_count:
                        self._evict(k)
                        break

    def _evict(self, key: str):
        self.cache.pop(key, None)
        self.order.pop(key, None)


def memoize(maxsize: Optional[int] = None, policy: str = "lru", ttl: Optional[float] = None):
    """Декоратор для мемоізації функцій"""
    memo = Memoizer(maxsize=maxsize, policy=policy, ttl=ttl)
    return memo
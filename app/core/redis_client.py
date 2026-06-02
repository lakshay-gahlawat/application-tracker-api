from unittest.mock import MagicMock
import os


class LazyRedisClient:
    """
    Wraps Redis so the connection is only made on first use.
    During testing (TESTING=true) returns a MagicMock instead.
    """
    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            if os.getenv("TESTING") == "true":
                self._client = MagicMock()
            else:
                import redis
                from app.core.config import REDIS_URL
                self._client = redis.Redis.from_url(
                    REDIS_URL,
                    decode_responses=True
                )
        return self._client

    def get(self, key):
        if os.getenv("TESTING") == "true":
            return None
        return self._get_client().get(key)

    def set(self, key, value):
        return self._get_client().set(key, value)

    def setex(self, key, time, value):
        return self._get_client().setex(key, time, value)

    def delete(self, *keys):
        return self._get_client().delete(*keys)


redis_client = LazyRedisClient()
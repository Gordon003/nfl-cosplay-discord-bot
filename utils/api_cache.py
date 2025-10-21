import hashlib
import os
import pickle
from datetime import datetime, timedelta
from loguru import logger


class APICache:

    def __init__(self, cache_dir="./cache", expiration_hours=24):
        self.cache_dir = cache_dir
        self.expiration_delta = timedelta(hours=expiration_hours)

        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def _get_cache_key(self, url, params=None):
        key_data = f"{url}_{str(params)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, url, params=None):
        cache_key = self._get_cache_key(url, params)
        cache_path = os.path.join(self.cache_dir, cache_key)

        if os.path.exists(cache_path):
            try:
                with open(cache_path, "rb") as f:
                    cached_data = pickle.load(f)

                # check if cache is expired
                if datetime.now() - cached_data["timestamp"] < self.expiration_delta:
                    return cached_data["data"]
                else:
                    logger.info(f"Cache expired for {url}")
            except Exception as e:
                logger.error(f"Error loading cache: {e}")

        return None

    def set(self, url, data, params=None):
        cache_key = self._get_cache_key(url, params)
        cache_file = os.path.join(self.cache_dir, cache_key)

        try:
            cache_data = {"timestamp": datetime.now(), "data": data}
            with open(cache_file, "wb") as f:
                pickle.dump(cache_data, f)
            return True
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
            return False

    def clear(self, url=None, params=None):
        if url:
            cache_key = self._get_cache_key(url, params)
            cache_file = os.path.join(self.cache_dir, cache_key)
            if os.path.exists(cache_file):
                os.remove(cache_file)
                return True
        else:
            for file in os.listdir(self.cache_dir):
                os.remove(os.path.join(self.cache_dir, file))
            logger.info("Cache cleared")
            return True
        return False

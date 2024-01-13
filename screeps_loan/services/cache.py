from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
import os

cache_root = os.environ["CACHE_ROOT"]

cache_opts = {
    "cache.type": "dbm",
    "cache.data_dir": cache_root + "/data",
    "cache.expire": 3600,
    "cache.lock_dir": cache_root + "/lock",
}

cache = CacheManager(**parse_cache_config_options(cache_opts))

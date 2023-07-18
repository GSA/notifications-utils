from datetime import datetime

from .request_cache import RequestCache  # noqa: F401 (unused import)


def daily_total_cache_key():
    return "{}-{}".format(datetime.utcnow().strftime("%Y-%m-%d"), "total")


def rate_limit_cache_key(service_id, api_key_type):
    return "{}-{}".format(str(service_id), api_key_type)

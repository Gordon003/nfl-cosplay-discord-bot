import requests
from loguru import logger

def cached_request(
    cache, method, url, headers=None, params=None, json=None, use_cache=True, api_timeout=30
):
    """Make a request with caching for GET requests"""
    logger.debug(f"Making request: {url}")
    if method.lower() == "get" and use_cache:
        # Try to get from cache first
        cached_response = cache.get(url, params)
        if cached_response is not None:
            logger.debug(f"CACHE HIT: {url}")
            return cached_response
        logger.debug(f"CACHE MISS: {url}")
    # Make request - raise exception if timed out
    try:
        if method.lower() == "get":
            response = requests.get(url, headers=headers, params=params, timeout=api_timeout)
        elif method.lower() == "post":
            response = requests.post(url, headers=headers, params=params, json=json, timeout=api_timeout)
    except Exception as e:
        raise Exception(f"Request failed with error: {e}")
    # Cache successful GET responses
    if method.lower() == "get" and response.status_code == 200 and use_cache:
        try:
            result = response.json()
            cache.set(url, result, params)
            logger.debug(f"CACHE SAVED: {url}")
            return result
        except Exception as e:
            logger.error(f"Error parsing JSON or caching: {str(e)}")
            return None
    elif response.status_code == 200:
        try:
            return response.json()
        except Exception as e:
            logger.error(f"Error parsing JSON: {str(e)}")
            return None
    else:
        logger.error(f"Request failed: {response.status_code} - {response.text}")
        return None
    
def format_time(seconds):
    """Format time in seconds to a human-readable string"""
    if seconds < 1:
        return "< 1 second"
    elif seconds < 60:
        return f"{seconds:.0f} seconds"
    else:
        minutes = int(seconds // 60)
        sec = int(seconds % 60)
        if sec == 0:
            return f"~{minutes} minutes"
        else:
            return f"~{minutes}.{sec // 6} minutes"


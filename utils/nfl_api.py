import os
import pickle
from loguru import logger
import requests
import json

from utils.api_cache import APICache
class NFLAPIManager:

    def __init__(self, cache_dir="./cache", match_cache_dir="./match_cache", expiration_hours=24):

        self.apiCache = APICache(cache_dir, expiration_hours)

        # Set up cache directory for match data
        self.match_cache_dir = match_cache_dir
        if not os.path.exists(match_cache_dir):
            os.makedirs(match_cache_dir)    

        self.current_year = os.getenv('CURRENT_YEAR')
        self.league = 'NFL'

        self.nfl_ncca_api_headers = {
            "x-rapidapi-key": os.getenv('NFL_NCAA_HIGHLIGHT_API_KEY'),
            "x-rapidapi-host": os.getenv('NFL_NCAA_HIGHLIGHT_API_HOST')
        }
        self.base_nfl_ncca_api_url = f"https://{os.getenv('NFL_NCAA_HIGHLIGHT_API_HOST')}"

        self.nfl_api_headers = {
            "x-rapidapi-key": os.getenv('NFL_API_KEY'),
            "x-rapidapi-host": os.getenv('NFL_API_HOST')
        }
        self.base_nfl_api_url = f"https://{os.getenv('NFL_API_HOST')}"

    def _cached_request(self, method, url, headers=None, params=None, json=None, use_cache=True, api_timeout=30):
        """Make a request with caching for GET requests"""
        logger.debug(f"Making request: {url}")
        if method.lower() == "get" and use_cache:
            # Try to get from cache first
            cached_response = self.apiCache.get(url, params)
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
                self.apiCache.set(url, result, params)
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
        
    async def get_nfl_matches(self):
        """Get NFL matches from the API"""

        full_url = f"{self.base_nfl_ncca_api_url}/matches"

        params = {
            'league': self.league,
            'season': self.current_year
        }

        try:
            return self._cached_request("get", full_url, headers=self.nfl_ncca_api_headers, params=params)
        except Exception as e:
            logger.error(f"Failed to get NFL matches: {e}")
            raise Exception("Failed to get NFL matches")
        
    async def get_nfl_specific_match(self, matchid):
        """Get a specific NFL match by ID"""

        # check if matchid is already cached
        cache_file = os.path.join(self.match_cache_dir, f"{matchid}.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding='utf-8') as f:
                cached_data = json.load(f)
            logger.debug(f"Match {matchid} loaded from cache.")
            return cached_data

        # make request to API
        full_url = f"{self.base_nfl_ncca_api_url}/matches/{matchid}"
        try:
            response = self._cached_request("get", full_url, headers=self.nfl_ncca_api_headers)
        except Exception as e:
            logger.error(f"Failed to get NFL match {matchid}: {e}")
            raise Exception(f"Failed to get NFL match {matchid}")
        
        # Save finished match data to cache
        if response[0]["state"]["report"] == "Final":
            cache_file = os.path.join(self.match_cache_dir, f"{matchid}.json")
            with open(cache_file, "w", encoding='utf-8') as f:
                json.dump(response, f, indent=2, ensure_ascii=False)
            logger.debug(f"Match {matchid} cached successfully.")

        return response
        
    async def get_nfl_standings(self, conference=None):
        """Get NFL Standings by conference"""

        league_type = ''
        if conference is None:
            logger.error("Conference must be specified")
            return None
        elif conference == 'afc':
            league_type = 'American Football Conference'
        elif conference == 'nfc':
            league_type = 'National Football Conference'
        else:
            logger.error("Invalid conference specified")
            return None

        full_url = f"{self.base_nfl_ncca_api_url}/standings"
        params = {
            'leagueName': league_type,
            'leagueType': self.league,
            'year': self.current_year
        }

        try:
            return self._cached_request("get", full_url, headers=self.nfl_ncca_api_headers, params=params)
        except Exception as e:
            logger.error(f"Failed to get NFL Standings {conference}: {e}")
            raise Exception(f"Failed to get NFL Standings {conference}")
        
    async def get_nfl_team_injuries(self, team_id):
        """Get NFL team injuries by team id"""

        full_url = f"{self.base_nfl_api_url}/nfl-team-injuries"
        params = {
            'id': str(team_id)
        }
        logger.info(f"full_url: {full_url}")
        try:
            return self._cached_request("get", full_url, headers=self.nfl_api_headers, params=params)
        except Exception as e:
            logger.error(f"Failed to get NFL injuries for {team_id}: {e}")
            raise Exception(f"Failed to get NFL injuries for {team_id}")
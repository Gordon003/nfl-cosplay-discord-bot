import random
from loguru import logger
from utils.api_cache import APICache
from utils.read_json import (
    load_characters,
    load_nfl_team_character_mapping,
    load_nfl_teams,
    load_storyline,
)

DATA_CACHE_EXPIRATION_HOUR = 24

class DataManager:

    def __init__(self):
        super().__init__()

        # load static data
        try:
            self.nfl_teams_data = load_nfl_teams()
            self.nfl_team_character_mapping_data = load_nfl_team_character_mapping()
            self.characters_data = load_characters()
            self.storyline_data = load_storyline()
            logger.debug("✅ Loaded all static data")
        except Exception as e:
            logger.error(f"❌ Error loading static data: {e}")

        # load cache
        self.cache = APICache(cache_dir="./cache", expiration_hours=DATA_CACHE_EXPIRATION_HOUR)
        logger.debug("✅ Loaded API Cache")

    ### CHARACTERS AND NFL TEAMS ###

    def get_character_key_by_team_key(self, team_key):
        team_key_formatted = team_key.lower().replace(" ", "_")
        return self.nfl_team_character_mapping_data[team_key_formatted]

    def get_team_key_by_character_key(self, character_key):
        character_key_formatted = character_key.lower().replace(" ", "_")
        for team_key, char_key in self.nfl_team_character_mapping_data.items():
            if char_key == character_key_formatted:
                return team_key
        return None

    def get_teams_key_by_conference_and_division(self, conference=None, division=None):
        filtered_teams = list(self.nfl_teams_data.keys())
        if conference:
            filtered_teams = [
                team
                for team in filtered_teams
                if self.nfl_teams_data[team]["conference"] == conference.upper()
            ]
        if division:
            filtered_teams = [
                team
                for team in filtered_teams
                if self.nfl_teams_data[team]["division"] == division.capitalize()
            ]
        return [self.nfl_teams_data[team] for team in filtered_teams]

    def get_team_data_by_team_key(self, team_key):
        team_key_formatted = team_key.lower().replace(" ", "_")
        return self.nfl_teams_data.get(team_key_formatted, None)

    def get_character_data_by_character_key(self, character_key):
        character_key_formatted = character_key.lower().replace(" ", "_")
        return self.characters_data.get(character_key_formatted, None)

    def get_all_team_keys(self):
        return list(self.nfl_teams_data.keys())

    def get_all_character_keys(self):
        return list(self.characters_data.keys())

    ### STORYLINE ###
    def get_storyline_random_big_win(self):
        return random.choice(self.storyline_data["storylines"]["big_win"]["templates"])

    def get_storyline_random_small_win(self):
        return random.choice(
            self.storyline_data["storylines"]["small_win"]["templates"]
        )

    def get_storyline_random_tie(self):
        return random.choice(self.storyline_data["storylines"]["tie"]["templates"])

    def get_storyline_random_upcoming(self):
        return random.choice(self.storyline_data["storylines"]["upcoming"]["templates"])

    ### GAME EVENTS ###
    def get_game_event_random_touchdown(self):
        return random.choice(
            self.storyline_data["game_events"]["touchdown"]["templates"]
        )

    def get_game_event_random_interception(self):
        return random.choice(
            self.storyline_data["game_events"]["interception"]["templates"]
        )

    def get_game_event_random_field_goal(self):
        return random.choice(
            self.storyline_data["game_events"]["field_goal"]["templates"]
        )

    def get_game_event_random_missed_field_goal(self):
        return random.choice(
            self.storyline_data["game_events"]["missed_field_goal"]["templates"]
        )

    def get_game_event_random_fumble(self):
        return random.choice(self.storyline_data["game_events"]["fumble"]["templates"])

    def get_game_event_random_downs(self):
        return random.choice(
            self.storyline_data["game_events"]["turnover_on_downs"]["templates"]
        )

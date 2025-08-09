import random
from loguru import logger


def get_character_key_by_team_key(nfl_team_character_mapping_data, team_name):
    """Get character key assigned to a team"""
    team_key = team_name.lower().replace(' ', '_')
    return nfl_team_character_mapping_data[team_key]

def get_team_key_by_character_key(nfl_team_character_mapping_data, character_name):
    """Get team key assigned to a character"""
    character_key = character_name.lower().replace(' ', '_')
    for name in nfl_team_character_mapping_data.keys():
        if nfl_team_character_mapping_data[name] == character_key:
            return name
    return None


def get_team_by_conference_and_division(nfl_teams_data, conference, division):
    """Filter teams by conference and division"""
    filtered_teams = list(nfl_teams_data.keys())
    if conference:
        filtered_teams = [team for team in filtered_teams if nfl_teams_data[team]['conference'] == conference.upper()]
    if division:
        filtered_teams = [team for team in filtered_teams if nfl_teams_data[team]['division'] == division.capitalize()]
    return [nfl_teams_data[team] for team in filtered_teams]

def get_big_win_template(storyline_data):
    return random.choice(storyline_data["storylines"]["big_win"]["templates"])

def get_small_win_template(storyline_data):
    return random.choice(storyline_data["storylines"]["small_win"]["templates"])

def get_tie_template(storyline_data):
    return random.choice(storyline_data["storylines"]["tie"]["templates"])

def get_upcoming_template(storyline_data):
    return random.choice(storyline_data["storylines"]["upcoming"]["templates"])
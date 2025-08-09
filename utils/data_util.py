import random
from loguru import logger

def get_big_win_template(storyline_data):
    return random.choice(storyline_data["storylines"]["big_win"]["templates"])

def get_small_win_template(storyline_data):
    return random.choice(storyline_data["storylines"]["small_win"]["templates"])

def get_tie_template(storyline_data):
    return random.choice(storyline_data["storylines"]["tie"]["templates"])

def get_upcoming_template(storyline_data):
    return random.choice(storyline_data["storylines"]["upcoming"]["templates"])
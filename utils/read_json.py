import json
from loguru import logger

def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"❌ Teams file not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON for {file_path}: {e}")
        return None


def load_nfl_teams():
    """Load NFL teams from JSON file"""
    return load_json('data/nfl_teams.json')

def load_characters():
    """Load Characters from JSON file"""
    return load_json('data/characters.json')
    
def load_characters_nfl_mapping():
    """Load Characters x NFL Mapping from JSON file"""
    return load_json('data/character_nfl_mapping.json')

def load_storyline():
    """Load Storyline from JSON file"""
    return load_json('data/storyline.json')
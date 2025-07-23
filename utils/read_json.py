import json

def load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Teams file not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON for {file_path}: {e}")
        return None


def load_nfl_teams():
    """Load NFL teams from JSON file"""
    return load_json('data/nfl_teams.json')

def load_total_drama_characters():
    """Load TD Characters from JSON file"""
    return load_json('data/total_drama_characters.json')
    
def load_characters_nfl_mapping():
    """Load TD Characters x NFL Mapping from JSON file"""
    return load_json('data/character_nfl_mapping.json')
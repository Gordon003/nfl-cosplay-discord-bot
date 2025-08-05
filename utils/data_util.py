def get_character_key_by_team(characters_nfl_mapping_data, team_name):
    """Get character key assigned to a team"""
    team_key = team_name.lower().replace(' ', '_')
    for name in characters_nfl_mapping_data.keys():
        if characters_nfl_mapping_data[name]["assigned_team"] == team_key:
            return name
    return None
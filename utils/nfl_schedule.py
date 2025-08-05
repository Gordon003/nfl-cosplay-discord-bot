from datetime import datetime
from time import timezone

from requests_cache import timedelta

def get_next_scheduled_games_by_team_id(games_list, team_id, num_games=5):
    """Filter upcoming scheduled game where the specified team is playing"""
    games = [
        game for game in games_list 
        if game["state"]["description"] == "Scheduled" and (game['homeTeam']['id'] == team_id or game['awayTeam']['id'] == team_id)
    ]
    return sorted(games, key=lambda game: datetime.fromisoformat(game['date'].replace('Z', '+00:00')))[:num_games]

def get_gameweek_by_offset(games_data, offset=0):
    """
    Get games of a specific week (This Thursday - Next Tuesday)
    
    Args:
        games_data: List of game objects
        offset: Week offset (0=current week, -1=last week, 1=next week, etc.)
    """
    
    # Get current date
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Find target Thursday
    days_since_thursday = (today.weekday() - 3) % 7
    current_thursday = today - timedelta(days=days_since_thursday)
    target_thursday = current_thursday + timedelta(weeks=offset)
    
    # Calculate target Tuesday (5 days after Thursday)
    target_tuesday = target_thursday + timedelta(days=4)
    
    # Filter games within the Thursday-Tuesday range
    week_games = []
    for game in games_data:
        try:
            # Parse game date - handle the UTC format
            game_date_str = game['date']
            game_date_str = game_date_str[:-1] + '+00:00'
            game_date = datetime.fromisoformat(game_date_str)
            game_date_naive = game_date.replace(tzinfo=None)
            
            # Check if game is in our target week
            if target_thursday <= game_date_naive <= target_tuesday:
                week_games.append(game)
                    
        except (ValueError, KeyError) as e:
            # Skip games with invalid date format
            print(f"Skipping game with invalid date: {game.get('date', 'No date')}")
            continue
    
    # Sort by date
    week_games.sort(key=lambda x: x['date'])

    return week_games
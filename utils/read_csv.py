import csv

def read_from_csv(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', newline='') as file:
            csv_reader = csv.reader(file)
            return [row for row in csv_reader]
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return []
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return []

def get_teams_info():
    return read_from_csv('data/nfl_teams.csv')

def get_teams_character():
    return read_from_csv('data/nfl_teams_character.csv')
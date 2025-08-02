from datetime import datetime

def convert_date(iso_date_string):
    # Parse the ISO format
    dt = datetime.fromisoformat(iso_date_string.replace('Z', '+00:00'))
    
    # Convert to readable format
    return dt.strftime("%B %d, %Y")
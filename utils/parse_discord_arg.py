import shlex
from typing import Optional, Union

class DiscordArgumentNotFoundError(Exception):
    """Custom exception for when a required argument is not found."""
    pass

def parse_discord_argument(command_string: str, flag: str) -> Optional[str]:
    """
    Parse Discord command arguments and extract value for a specific flag.
    
    Args:
        command_string (str): The full command string from Discord message
        flag (str): The flag to search for (e.g., '--sort-by')
    
    Returns:
        str: The value associated with the flag, or None if flag exists but no value
    
    Raises:
        DiscordArgumentNotFoundError: If the flag is not found in the command string
        
    Examples:
        >>> parse_discord_argument("!command --sort-by name --limit 10", "--sort-by")
        'name'
        >>> parse_discord_argument("!command --sort-by --limit 10", "--sort-by")
        None
        >>> parse_discord_argument("!command --limit 10", "--sort-by")
        ArgumentNotFoundError: Argument '--sort-by' not found
    """
    try:
        # Use shlex to properly handle quoted arguments and spaces
        args = shlex.split(command_string)
    except ValueError as e:
        # Handle malformed quotes
        raise DiscordArgumentNotFoundError(f"Malformed command string: {e}")
    
    # Check if flag exists in arguments
    if flag not in args:
        raise DiscordArgumentNotFoundError(f"Argument '{flag}' not found")
    
    # Find the index of the flag
    flag_index = args.index(flag)
    
    # Check if there's a value after the flag
    if flag_index + 1 < len(args):
        next_arg = args[flag_index + 1]
        # If next argument is another flag (starts with -), return None
        if next_arg.startswith('-'):
            return None
        return next_arg
    else:
        # Flag is at the end, no value provided
        return None

def parse_multiple_arguments(command_string: str, flags: list) -> dict:
    """
    Parse multiple flags from a Discord command string.
    
    Args:
        command_string (str): The full command string from Discord message
        flags (list): List of flags to search for
    
    Returns:
        dict: Dictionary with flag names as keys and their values (or None/Exception)
    """
    results = {}
    
    for flag in flags:
        try:
            results[flag] = parse_discord_argument(command_string, flag)
        except ArgumentNotFoundError as e:
            results[flag] = e
    
    return results

# Example usage and test cases
if __name__ == "__main__":
    # Test cases
    test_commands = [
        "!search --sort-by name --limit 10",
        "!search --sort-by --limit 10",
        "!search --limit 10",
        "!search --sort-by 'newest first' --order desc",
        "!search --sort-by",
        '!search --query "hello world" --sort-by date'
    ]
    
    print("Testing parse_discord_argument function:")
    print("-" * 50)
    
    for cmd in test_commands:
        print(f"\nCommand: {cmd}")
        try:
            result = parse_discord_argument(cmd, "--sort-by")
            print(f"Result: {repr(result)}")
        except ArgumentNotFoundError as e:
            print(f"Exception: {e}")
    
    print("\n" + "=" * 50)
    print("Testing multiple arguments:")
    
    cmd = "!search --sort-by name --limit 10 --order desc --verbose"
    flags_to_check = ["--sort-by", "--limit", "--missing-flag", "--verbose"]
    
    results = parse_multiple_arguments(cmd, flags_to_check)
    for flag, result in results.items():
        if isinstance(result, Exception):
            print(f"{flag}: Exception - {result}")
        else:
            print(f"{flag}: {repr(result)}")
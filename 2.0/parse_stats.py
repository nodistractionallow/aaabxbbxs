# parse_stats.py
import json
import sys

def find_and_print_williamson_bowling_stats(json_string_arg):
    print(f"DEBUG: Received JSON string argument (first 500 chars): {json_string_arg[:500]}")
    if not json_string_arg or not json_string_arg.strip():
        print("Error: JSON string argument is empty or contains only whitespace.")
        return

    try:
        data = json.loads(json_string_arg)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Problematic JSON string (first 500 chars): {json_string_arg[:500]}")
        return

    williamson_stats_entry = None
    player_found = False
    player_name_to_find = "KS Williamson"

    if not isinstance(data, dict):
        print("Error: JSON data is not in the expected dictionary format (top level should be a dict of players).")
        return

    # Attempt to find the player by various common keying/naming conventions
    # Case 1: Player's full name "KS Williamson" is used as a key
    if player_name_to_find in data:
        williamson_stats_entry = data[player_name_to_find]
        player_found = True

    # Case 2: Iterate through dictionary items, checking displayName or playerName
    if not player_found:
        for key, player_data in data.items():
            if isinstance(player_data, dict):
                if player_data.get('displayName') == player_name_to_find or \
                   player_data.get('playerName') == player_name_to_find:
                    williamson_stats_entry = player_data
                    player_found = True
                    break
                # Check if the key itself is the initials "KSW" or if playerInitials field is "KSW"
                if key == "KSW" or player_data.get('playerInitials') == "KSW":
                    if player_data.get('displayName', player_data.get('playerName')) == player_name_to_find or \
                       not (player_data.get('displayName') or player_data.get('playerName')):
                         williamson_stats_entry = player_data
                         player_found = True
                         break


    if player_found and williamson_stats_entry:
        bowling_stats_to_extract = [
            'bowlAverage', 'bowlBalls', 'bowlDotRate', 'bowlEco',
            'bowlMaidens', 'bowlRuns', 'bowlSR', 'bowlWickets',
            'bowlWicketsRate', 'bowlBallsTotalRate'
        ]

        print(f"Bowling Stats for KS Williamson:")
        stats_found_count = 0

        source_stats = williamson_stats_entry
        if 'bowlingStats' in williamson_stats_entry and isinstance(williamson_stats_entry['bowlingStats'], dict):
            source_stats = williamson_stats_entry['bowlingStats']

        for stat_name in bowling_stats_to_extract:
            if stat_name in source_stats:
                stat_value = source_stats[stat_name]
                print(f"  {stat_name}: {stat_value if stat_value is not None else 'Not Available (null)'}")
                stats_found_count += 1

        if stats_found_count == 0:
            print(f"  No specific bowling statistics (bowlAverage, bowlBalls, etc.) were found for KS Williamson in the identified entry.")
            print(f"  This could mean they haven't bowled, or the stats are not recorded under the expected field names in the 'source_stats' dictionary used.")
    else:
        print(f"Player '{player_name_to_find}' not found in the provided JSON data using direct name match, displayName, playerName, or common initials 'KSW'.")

if __name__ == "__main__":
    json_input_string = None
    if len(sys.argv) > 1:
        if sys.argv[1] == '-': # Read from stdin if argument is '-'
            print("DEBUG: Reading JSON from stdin.")
            json_input_string = sys.stdin.read()
        else: # Read from the first command-line argument
            print("DEBUG: Reading JSON from command-line argument.")
            json_input_string = sys.argv[1]
        find_and_print_williamson_bowling_stats(json_input_string)
    else: # No arguments, try reading from stdin as a fallback
        print("DEBUG: No command-line argument, attempting to read JSON from stdin.")
        json_input_string = sys.stdin.read()
        if json_input_string: # If something was read from stdin
             find_and_print_williamson_bowling_stats(json_input_string)
        else:
            print("Error: No JSON string provided via command-line argument or stdin.")

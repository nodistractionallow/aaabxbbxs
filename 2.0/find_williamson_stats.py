import json
import sys

# The JSON string is embedded here
PLAYER_INFO_JSON_STRING = """
{
  "RINKU SINGH": {
    "_id": "317293",
    "playerInitials": "R SINGH",
    "displayName": "RINKU SINGH",
    "batStyle": "right-hand bat",
    "bowlStyle": "right-arm medium",
    "batRunsTotal": 555,
    "batBallsTotal": 300,
    "bowlRunsTotal": 355,
    "bowlBallsTotal": 142,
    "batOutsTotal": 7,
    "bowlOutsTotal": 5,
    "bowlNoballs": 2,
    "bowlWides": 3,
    "catches": 10,
    "batOutTypes": {
      "caught": 10,
      "runOut": 0,
      "bowled": 5,
      "lbw": 1,
      "hitwicket": 0,
      "stumped": 0
    },
    "bowlOutTypes": {
      "caught": 3,
      "runOut": 0,
      "bowled": 2,
      "lbw": 0,
      "hitwicket": 0,
      "stumped": 0
    },
    "batRunDenominations": {
      "0": 33,
      "1": 50,
      "2": 20,
      "3": 0,
      "4": 12,
      "5": 0,
      "6": 17
    },
    "bowlRunDenominations": {
      "0": 7,
      "1": 1,
      "2": 11,
      "3": 0,
      "4": 15,
      "5": 0,
      "6": 11
    },
    "overNumbers": ["13", "11"],
    "runnedOut": 0,
    "position": ["null"],
    "byBatsman": {
      "left-hand bat": {
        "bowlRunsTotal": 119,
        "bowlBallsTotal": 78,
        "bowlOutsTotal": 0,
        "bowlOutTypes": {
          "caught": 0,
          "runOut": 0,
          "bowled": 0,
          "lbw": 0,
          "hitwicket": 0,
          "stumped": 0
        },
        "bowlRunDenominations": {
          "0": 3,
          "1": 1,
          "2": 1,
          "3": 0,
          "4": 4,
          "5": 0,
          "6": 0
        }
      },
      "right-hand bat": {
        "bowlRunsTotal": 210,
        "bowlBallsTotal": 94,
        "bowlOutsTotal": 0,
        "bowlOutTypes": {
          "caught": 0,
          "runOut": 0,
          "bowled": 0,
          "lbw": 0,
          "hitwicket": 0,
          "stumped": 0
        },
        "bowlRunDenominations": {
          "0": 4,
          "1": 0,
          "2": 0,
          "3": 0,
          "4": 1,
          "5": 0,
          "6": 1
        }
      }
    },

    "captained": 0,
    "wicketkeeper": 0,
    "matches": 17
  },
"TILAK VERMA": {
    "_id": "1151278",
    "playerInitials": "T VERMA",
    "displayName": "TILAK VERMA",
    "batStyle": "left-hand bat",
    "bowlStyle": "legbreak",
    "batRunsTotal": 706,
    "batBallsTotal": 394,
    "bowlRunsTotal": 0,
    "bowlBallsTotal": 0,
    "batOutsTotal": 12,
    "bowlOutsTotal": 0,
    "bowlNoballs": 0,
    "bowlWides": 0,
    "catches": 2,
    "batOutTypes": {
      "caught": 7,
      "runOut": 2,
      "bowled": 2,
      "lbw": 1,
      "hitwicket": 0,
      "stumped": 0
    },
    "bowlOutTypes": {
      "caught": 0,
      "runOut": 0,
      "bowled": 0,
      "lbw": 0,
      "hitwicket": 0,
      "stumped": 0
    },
    "batRunDenominations": {
      "0": 43,
      "1": 34,
      "2": 32,
      "3": 0,
      "4": 51,
      "5": 0,
      "6": 44
    },
    "bowlRunDenominations": {
      "0": 0,
      "1": 0,
      "2": 0,
      "3": 0,
      "4": 0,
      "5": 0,
      "6": 0
    },
    "overNumbers": [],
    "runnedOut": 0,
    "position": [0, "null", "null", "null", 0, 0],
    "byBatsman": {},
    "byBowler": {
      "right-arm medium": {
        "batRunsTotal": 227,
        "batBallsTotal": 124,
        "batOutsTotal": 1,
        "batOutTypes": {
          "caught": 0,
          "runOut": 0,
          "bowled": 1,
          "lbw": 0,
          "hitwicket": 0,
          "stumped": 0
        },
        "batRunDenominations": {
          "0": 11,
          "1": 9,
          "2": 1,
          "3": 0,
          "4": 1,
          "5": 0,
          "6": 2
        }
      },
      "left-arm medium-fast": {
        "batRunsTotal": 91,
        "batBallsTotal": 41,
        "batOutsTotal": 0,
        "batOutTypes": {
          "caught": 0,
          "runOut": 0,
          "bowled": 0,
          "lbw": 0,
          "hitwicket": 0,
          "stumped": 0
        },
        "batRunDenominations": {
          "0": 0,
          "1": 1,
          "2": 0,
          "3": 0,
          "4": 0,
          "5": 0,
          "6": 0
        }
      },
      "right-arm fast": {
        "batRunsTotal": 425,
        "batBallsTotal": 219,
        "batOutsTotal": 0,
        "batOutTypes": {
          "caught": 0,
          "runOut": 0,
          "bowled": 0,
          "lbw": 0,
          "hitwicket": 0,
          "stumped": 0
        },
        "batRunDenominations": {
          "0": 8,
          "1": 7,
          "2": 0,
          "3": 0,
          "4": 3,
          "5": 0,
          "6": 1
        }
      },
      "right-arm offbreak": {
        "batRunsTotal": 113,
        "batBallsTotal": 115,
        "batOutsTotal": 0,
        "batOutTypes": {
          "caught": 0,
          "runOut": 0,
          "bowled": 0,
          "lbw": 0,
          "hitwicket": 0,
          "stumped": 0
        },
        "batRunDenominations": {
          "0": 5,
          "1": 9,
          "2": 0,
          "3": 0,
          "4": 1,
          "5": 0,
          "6": 0
        }
      },
      "slow left-arm orthodox": {
        "batRunsTotal": 94,
        "batBallsTotal": 44,
        "batOutsTotal": 0,
        "batOutTypes": {
          "caught": 0,
          "runOut": 0,
          "bowled": 0,
          "lbw": 0,
          "hitwicket": 0,
          "stumped": 0
        },
        "batRunDenominations": {
          "0": 0,
          "1": 4,
          "2": 0,
          "3": 0,
          "4": 0,
          "5": 0,
          "6": 0
        }
      },
      "left-arm fast-medium": {
        "batRunsTotal": 77,
        "batBallsTotal": 57,
        "batOutsTotal": 1,
        "batOutTypes": {
          "caught": 1,
          "runOut": 0,
          "bowled": 0,
          "lbw": 0,
          "hitwicket": 0,
          "stumped": 0
        },
        "batRunDenominations": {
          "0": 4,
          "1": 1,
          "2": 1,
          "3": 0,
          "4": 1,
          "5": 0,
          "6": 0
        }
      },
      "right-arm fast-medium": {
        "batRunsTotal": 119,
        "batBallsTotal": 111,
        "batOutsTotal": 1,
        "batOutTypes": {
          "caught": 1,
          "runOut": 0,
          "bowled": 0,
          "lbw": 0,
          "hitwicket": 0,
          "stumped": 0
        },
        "batRunDenominations": {
          "0": 8,
          "1": 1,
          "2": 0,
          "3": 0,
          "4": 2,
          "5": 0,
          "6": 0
        }
      },
      "legbreak googly": {
        "batRunsTotal": 520,
        "batBallsTotal": 213,
        "batOutsTotal": 1,
        "batOutTypes": {
          "caught": 0,
          "runOut": 0,
          "bowled": 0,
          "lbw": 1,
          "hitwicket": 0,
          "stumped": 0
        },
        "batRunDenominations": {
          "0": 7,
          "1": 2,
          "2": 0,
          "3": 0,
          "4": 3,
          "5": 0,
          "6": 1
        }
      }
    },
    "captained": 0,
    "wicketkeeper": 0,
    "matches": 16
  },
  "Kane Williamson": {
    "_id": "277906",
    "playerInitials": "KS Williamson",
    "displayName": "Kane Williamson",
    "batStyle": "right-hand bat",
    "bowlStyle": "right-arm offbreak",
    "batRunsTotal": 1618,
    "batBallsTotal": 1194,
    "bowlRunsTotal": 31,
    "bowlBallsTotal": 18,
    "batOutsTotal": 38,
    "bowlOutsTotal": 0,
    "bowlNoballs": 0,
    "bowlWides": 0,
    "catches": 20,
    "batOutTypes": {
      "caught": 31,
      "runOut": 0,
      "bowled": 3,
      "lbw": 1,
      "hitwicket": 0,
      "stumped": 1
    },
    "bowlOutTypes": {
      "caught": 0,
      "runOut": 0,
      "bowled": 0,
      "lbw": 0,
      "hitwicket": 0,
      "stumped": 0
    },
    "batRunDenominations": {
      "0": 381,
      "1": 552,
      "2": 87,
      "3": 7,
      "4": 137,
      "5": 1,
      "6": 53
    },
    "bowlRunDenominations": {
      "0": 2,
      "1": 11,
      "2": 2,
      "3": 0,
      "4": 1,
      "5": 0,
      "6": 2
    },
    "overNumbers": ["10", "12", "5"],
    "runnedOut": 2,
    "position": [
      1, 1, 1, 1, 1, "null", 1, "null", "null", "null", "null", "null", 0, 0, 1, "null", 1, "null", 1, "null", 1, 1, 1, 1, "null", "null", "null", "null", 0, 3, "null", 2, 2, "null", 2, "null", 2, 2, "null", 2, "null", 3, "null", "null", 1, "null", 1, 1, 1, "null", "null", "null", 2, "null"
    ],
    "byBatsman": {
      "left-hand bat": {
        "bowlRunsTotal": 31,
        "bowlBallsTotal": 18,
        "bowlOutsTotal": 0,
        "bowlOutTypes": { "caught": 0, "runOut": 0, "bowled": 0, "lbw": 0, "hitwicket": 0, "stumped": 0 },
        "bowlRunDenominations": { "0": 2, "1": 11, "2": 2, "3": 0, "4": 1, "5": 0, "6": 2 }
      }
    },
    "byBowler": {
      "right-arm offbreak": { "batRunsTotal": 187, "batBallsTotal": 157, "batOutsTotal": 1, "batOutTypes": { "caught": 1, "runOut": 0, "bowled": 0, "lbw": 0, "hitwicket": 0, "stumped": 0 }, "batRunDenominations": { "0": 50, "1": 80, "2": 13, "3": 0, "4": 9, "5": 0, "6": 7 } },
      "right-arm fast-medium": { "batRunsTotal": 196, "batBallsTotal": 133, "batOutsTotal": 8, "batOutTypes": { "caught": 5, "runOut": 0, "bowled": 2, "lbw": 1, "hitwicket": 0, "stumped": 0 }, "batRunDenominations": { "0": 47, "1": 49, "2": 15, "3": 0, "4": 18, "5": 0, "6": 7 } },
      "left-arm fast-medium": { "batRunsTotal": 59, "batBallsTotal": 45, "batOutsTotal": 2, "batOutTypes": { "caught": 2, "runOut": 0, "bowled": 0, "lbw": 0, "hitwicket": 0, "stumped": 0 }, "batRunDenominations": { "0": 14, "1": 22, "2": 2, "3": 0, "4": 8, "5": 0, "6": 0 } },
      "right-arm fast": { "batRunsTotal": 317, "batBallsTotal": 197, "batOutsTotal": 5, "batOutTypes": { "caught": 5, "runOut": 0, "bowled": 0, "lbw": 0, "hitwicket": 0, "stumped": 0 }, "batRunDenominations": { "0": 63, "1": 77, "2": 18, "3": 2, "4": 29, "5": 1, "6": 12 } },
      "right-arm medium": { "batRunsTotal": 263, "batBallsTotal": 170, "batOutsTotal": 6, "batOutTypes": { "caught": 6, "runOut": 0, "bowled": 0, "lbw": 0, "hitwicket": 0, "stumped": 0 }, "batRunDenominations": { "0": 64, "1": 57, "2": 11, "3": 2, "4": 33, "5": 0, "6": 7 } },
      "legbreak": { "batRunsTotal": 134, "batBallsTotal": 117, "batOutsTotal": 2, "batOutTypes": { "caught": 1, "runOut": 0, "bowled": 1, "lbw": 0, "hitwicket": 0, "stumped": 0 }, "batRunDenominations": { "0": 30, "1": 70, "2": 5, "3": 0, "4": 9, "5": 0, "6": 3 } },
      "legbreak googly": { "batRunsTotal": 120, "batBallsTotal": 102, "batOutsTotal": 3, "batOutTypes": { "caught": 2, "runOut": 0, "bowled": 0, "lbw": 0, "hitwicket": 0, "stumped": 1 }, "batRunDenominations": { "0": 30, "1": 63, "2": 3, "3": 0, "4": 3, "5": 0, "6": 6 } },
      "slow left-arm orthodox": { "batRunsTotal": 116, "batBallsTotal": 85, "batOutsTotal": 0, "batOutTypes": { "caught": 0, "runOut": 0, "bowled": 0, "lbw": 0, "hitwicket": 0, "stumped": 0 }, "batRunDenominations": { "0": 13, "1": 55, "2": 6, "3": 1, "4": 7, "5": 0, "6": 3 } },
      "left-arm wrist-spin": { "batRunsTotal": 49, "batBallsTotal": 41, "batOutsTotal": 2, "batOutTypes": { "caught": 2, "runOut": 0, "bowled": 0, "lbw": 0, "hitwicket": 0, "stumped": 0 }, "batRunDenominations": { "0": 12, "1": 21, "2": 3, "3": 0, "4": 4, "5": 0, "6": 1 } },
      "left-arm medium": { "batRunsTotal": 61, "batBallsTotal": 38, "batOutsTotal": 1, "batOutTypes": { "caught": 1, "runOut": 0, "bowled": 0, "lbw": 0, "hitwicket": 0, "stumped": 0 }, "batRunDenominations": { "0": 14, "1": 12, "2": 6, "3": 1, "4": 5, "5": 0, "6": 2 } },
      "left-arm fast": { "batRunsTotal": 0, "batBallsTotal": 1, "batOutsTotal": 1, "batOutTypes": { "caught": 1, "runOut": 0, "bowled": 0, "lbw": 0, "hitwicket": 0, "stumped": 0 }, "batRunDenominations": { "0": 1, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0 } },
      "right-arm medium-fast": { "batRunsTotal": 104, "batBallsTotal": 72, "batOutsTotal": 4, "batOutTypes": { "caught": 4, "runOut": 0, "bowled": 0, "lbw": 0, "hitwicket": 0, "stumped": 0 }, "batRunDenominations": { "0": 26, "1": 31, "2": 4, "3": 0, "4": 11, "5": 0, "6": 3 } },
      "left-arm medium-fast": { "batRunsTotal": 37, "batBallsTotal": 36, "batOutsTotal": 1, "batOutTypes": { "caught": 1, "runOut": 0, "bowled": 0, "lbw": 0, "hitwicket": 0, "stumped": 0 }, "batRunDenominations": { "0": 17, "1": 15, "2": 1, "3": 1, "4": 1, "5": 0, "6": 2 } }
    },
    "captained": 25,
    "wicketkeeper": 0,
    "matches": 54
  }
}
"""

def find_player_and_print_bowling_stats(json_data_string):
    """
    Parses an embedded JSON string, finds "Kane Williamson" (with flexibility),
    and prints all his bowling-related statistics.
    """
    try:
        data = json.loads(json_data_string)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return

    player_to_find_primary = "Kane Williamson"
    player_to_find_secondary = "KS Williamson"
    player_initials_alt = "KSW"

    player_entry = None
    player_found = False
    actual_player_name_found = None

    if player_to_find_primary in data:
        player_entry = data[player_to_find_primary]
        player_found = True
        actual_player_name_found = player_to_find_primary
    elif player_to_find_secondary in data:
        player_entry = data[player_to_find_secondary]
        player_found = True
        actual_player_name_found = player_to_find_secondary
    else:
        for key, value in data.items():
            if isinstance(value, dict):
                displayName = value.get("displayName")
                playerName = value.get("playerName")
                initials = value.get("playerInitials")

                if displayName == player_to_find_primary or playerName == player_to_find_primary or \
                   displayName == player_to_find_secondary or playerName == player_to_find_secondary:
                    player_entry = value
                    player_found = True
                    actual_player_name_found = displayName if displayName else playerName
                    break

                if initials == player_initials_alt:
                    # Confirm this entry is indeed for KS Williamson
                    if value.get("displayName") == player_to_find_primary or value.get("playerName") == player_to_find_primary or \
                       value.get("displayName") == player_to_find_secondary or value.get("playerName") == player_to_find_secondary:
                         player_entry = value
                         player_found = True
                         actual_player_name_found = displayName if displayName else playerName
                         break
                    elif not (value.get("displayName") or value.get("playerName")):
                         player_entry = value
                         player_found = True
                         actual_player_name_found = key # Use key if no other name found
                         break

    if not player_found:
        if player_initials_alt in data and isinstance(data[player_initials_alt], dict):
            temp_entry = data[player_initials_alt]
            # Check if this KSW entry is likely Kane Williamson
            if temp_entry.get("displayName", "").lower().startswith("kane") or \
               temp_entry.get("playerName", "").lower().startswith("kane") or \
               player_to_find_primary in temp_entry.get("displayName", "") or \
               player_to_find_secondary in temp_entry.get("displayName", ""):
                 player_entry = temp_entry
                 player_found = True
                 actual_player_name_found = player_initials_alt # Found by KSW key

    if player_found and player_entry:
        print(f"Bowling stats for {player_entry.get('displayName', actual_player_name_found)}:")

        bowling_stats_printed_count = 0

        collected_stats = {}
        for key, stat_value in player_entry.items():
            if key.startswith("bowl"):
                collected_stats[key] = stat_value

        if collected_stats:
            # Ensure the desired stats are printed if they exist
            bowling_stats_to_extract = [
                'bowlAverage', 'bowlBalls', 'bowlDotRate', 'bowlEco',
                'bowlMaidens', 'bowlRuns', 'bowlSR', 'bowlWickets',
                'bowlWicketsRate', 'bowlBallsTotalRate', 'bowlNoballs', 'bowlWides', 'bowlBallsTotal', 'bowlRunsTotal', 'bowlOutsTotal', 'bowlOutTypes', 'bowlRunDenominations'
            ]
            for stat_name in bowling_stats_to_extract:
                 if stat_name in collected_stats:
                    stat_value = collected_stats[stat_name]
                    print(f"  {stat_name}: {stat_value if stat_value is not None else 'Not Available'}")
                    bowling_stats_printed_count +=1

            # Print any other bowl* stats not explicitly listed above
            for stat_name, stat_value in sorted(collected_stats.items()):
                if stat_name not in bowling_stats_to_extract:
                    print(f"  {stat_name} (other): {stat_value if stat_value is not None else 'Not Available'}")
                    bowling_stats_printed_count +=1

        if bowling_stats_printed_count == 0:
            if player_entry.get("bowlBallsTotal", 0) == 0 and not any(key.startswith("bowl") for key in player_entry.keys()):
                 print(f"  {player_entry.get('displayName', actual_player_name_found)} has no bowling stats recorded (bowlBallsTotal is 0 or missing, and no 'bowl*' prefixed stats).")
            else: # Should be caught by the previous block if collected_stats is not empty
                print(f"  No specific 'bowl*' prefixed stats found for {player_entry.get('displayName', actual_player_name_found)}.")

    else:
        print(f"Player '{player_to_find_primary}' (or variations like '{player_to_find_secondary}') not found.")

if __name__ == "__main__":
    find_player_and_print_bowling_stats(PLAYER_INFO_JSON_STRING)

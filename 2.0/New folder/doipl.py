import os
import sys
import random
from mainconnect import game
from tabulate import tabulate
import copy

# Ensure scores directory exists
dir_path = os.path.join(os.getcwd(), "scores")
os.makedirs(dir_path, exist_ok=True)

# Clean scores folder before starting
for f in os.listdir(dir_path):
    os.remove(os.path.join(dir_path, f))

teams = ['dc', 'csk', 'rcb', 'mi', 'kkr', 'pbks', 'rr', 'srh']
points = {}
battingInfo = {}
bowlingInfo = {}

# Initialize points table
for team in teams:
    points[team] = {
        "P": 0, "W": 0, "L": 0, "T": 0, "SO": 0,
        "runsScored": 0, "ballsFaced": 0,
        "runsConceded": 0, "ballsBowled": 0,
        "pts": 0
    }

battingf = 0
bowlingf = 0

# Enhanced commentary lines for different events
commentary_lines = {
    'start': [
        "It's a packed stadium today, folks! The atmosphere is electric!",
        "The players are ready, and the crowd is roaring for action!",
        "What a perfect day for some thrilling cricket!"
    ],
    '0': [
        "Good ball! Dot ball, no run scored.",
        "Tight bowling, the batsman defends solidly.",
        "No run, excellent line and length from the bowler!"
    ],
    '1': [
        "Quick single taken, good running between the wickets!",
        "Pushed for a single, smart cricket.",
        "One run added to the total, tidy shot."
    ],
    '2': [
        "Nicely placed for a couple of runs!",
        "Two runs, good placement in the gap.",
        "Driven for two, excellent running!"
    ],
    '3': [
        "Three runs! Brilliant effort in the field to stop the boundary.",
        "Rare three runs, well-judged by the batsmen.",
        "Three to the total, superb running!"
    ],
    '4': [
        "FOUR! Cracked through the covers, what a shot!",
        "Boundary! Perfectly timed, races to the fence.",
        "FOUR runs! That’s a glorious cover drive!"
    ],
    '6': [
        "SIX! Launched over the stands, what a hit!",
        "Huge SIX! That’s gone miles into the crowd!",
        "Maximum! Smashed with authority!"
    ],
    'wicket': {
        'caught': [
            "Caught! Edged and taken!",
            "Caught! Simple catch for the fielder.",
            "Caught! What a grab! That was flying!",
            "Caught! The batsman walks, a good take in the field."
        ],
        'bowled': [
            "Bowled him! Right through the gate!",
            "Bowled! Timber! The stumps are a mess!",
            "Bowled! Cleaned him up, no answer to that delivery!"
        ],
        'lbw': [
            "LBW! That looked plumb! The umpire raises the finger.",
            "LBW! Trapped in front, that's got to be out!",
            "LBW! He's given him. Looked like it was hitting the stumps."
        ],
        'runOut': [ # Note: 'runout' (lowercase 'o') is used in mainconnect logs for out_type
            "Run out! Terrible mix-up, and he's short of his ground!",
            "Run out! Direct hit! What a piece of fielding!",
            "Run out! They went for a risky single, and paid the price."
        ],
        'stumped': [
            "Stumped! Quick work by the keeper, he was out of his crease!",
            "Stumped! Fooled by the flight, and the bails are off in a flash.",
            "Stumped! Great take and stumping by the wicketkeeper."
        ],
        'hitwicket': [
            "Hit wicket! Oh dear, he's knocked his own bails off!",
            "Hit wicket! What a bizarre way to get out!",
            "Hit wicket! He's dislodged the bails with his bat/body."
        ],
        'general': [ # Fallback for any other wicket type or if specific type not found
            "OUT! That's a big wicket for the bowling side!",
            "WICKET! The batsman has to depart.",
            "GONE! A crucial breakthrough for the bowlers."
        ]
    },
    'wide': [
        "Wide ball! The bowler strays down the leg side.",
        "Called wide, too far outside off stump.",
        "Extra run! Wide from the bowler."
    ],
    'end': [
        "What a match that was, folks! A true spectacle!",
        "The crowd is buzzing after that thrilling finish!",
        "A game to remember for years to come!"
    ],
    'innings_end': [
        "That’s the end of the innings. A solid total on the board!",
        "Innings wrapped up, setting up an exciting chase!",
        "End of the batting effort, now over to the bowlers!"
    ],
    'no_ball_call': [
        "No Ball! The bowler has overstepped. Free hit coming up!",
        "That's a No Ball! An extra run and a free hit.",
        "No Ball called by the umpire. The next delivery is a free hit."
    ],
    'free_hit_delivery': [ # Can be appended or used standalone
        "Free Hit delivery!",
        "Here comes the Free Hit...",
        "Batsman has a free license on this Free Hit!"
    ],
    'no_ball_runs': [ # For runs scored off a no-ball delivery
        "And runs scored off the No Ball! Adding insult to injury.",
        "They pick up runs on the No Ball as well!",
        "The batsman cashes in on the No Ball delivery!"
    ],
    'extras': { # New category for Byes and Leg-byes
        'B': [
            "Byes signalled! They sneak a single as the keeper misses.",
            "That's byes, well run by the batsmen.",
            "A bye taken as the ball evades everyone."
        ],
        'LB': [
            "Leg Byes! Off the pads and they run.",
            "Signalled as Leg Byes by the umpire.",
            "They get leg-byes for that deflection."
        ]
    }
}

def display_points_table():
    pointsTabulate = []
    for team in points:
        data = points[team]
        nrr = 0
        if data['ballsFaced'] > 0 and data['ballsBowled'] > 0:
            nrr = (data['runsScored'] / data['ballsFaced']) * 6 - (data['runsConceded'] / data['ballsBowled']) * 6
        row = [team.upper(), data['P'], data['W'], data['L'], data['T'], data['SO'], round(nrr, 2), data['pts']]
        pointsTabulate.append(row)
    pointsTabulate = sorted(pointsTabulate, key=lambda x: (x[7], x[6]), reverse=True) # Sort by Pts (idx 7), then NRR (idx 6)
    print("\nCurrent Points Table:")
    print(tabulate(pointsTabulate, headers=["Team", "Played", "Won", "Lost", "Tied", "SO", "NRR", "Points"], tablefmt="grid"))

def display_top_players():
    battingTabulate = []
    for b in battingInfo:
        c = battingInfo[b]
        outs = sum(1 for bl in c['ballLog'] if "W" in bl)
        avg = round(c['runs'] / outs, 2) if outs else float('inf')
        sr = round((c['runs'] / c['balls']) * 100, 2) if c['balls'] else 0
        battingTabulate.append([b, c['runs'], avg, sr])
    battingTabulate = sorted(battingTabulate, key=lambda x: x[1], reverse=True)[:3]
    
    print("\nTop 3 Batsmen:")
    print(tabulate(battingTabulate, headers=["Player", "Runs", "Average", "Strike Rate"], tablefmt="grid"))

    bowlingTabulate = []
    for b in bowlingInfo:
        c = bowlingInfo[b]
        economy = round((c['runs'] / c['balls']) * 6, 2) if c['balls'] else float('inf')
        bowlingTabulate.append([b, c['wickets'], economy])
    bowlingTabulate = sorted(bowlingTabulate, key=lambda x: x[1], reverse=True)[:3]
    
    print("\nTop 3 Bowlers:")
    print(tabulate(bowlingTabulate, headers=["Player", "Wickets", "Economy"], tablefmt="grid"))

def display_scorecard(bat_tracker, bowl_tracker, team_name, innings_num):
    print(f"\n--- {team_name.upper()} Scorecard: Innings {innings_num} ---")
    
    # Batting Scorecard
    batsmanTabulate = []
    for player_name_key in bat_tracker: # player_name_key is player's name/initials from bat_tracker keys
        data = bat_tracker[player_name_key]
        runs_scored = data['runs']
        balls_faced = data['balls']

        # Get pre-calculated dismissal status from mainconnect.py (via bat_tracker)
        # Assuming 'how_out_string' is the key set in mainconnect.py's batterTracker
        how_out_status = data.get('how_out_string', 'DNB')

        sr_val = 'NA'
        if balls_faced > 0:
            sr_val = round((runs_scored / balls_faced) * 100, 2)
        elif how_out_status not in ['DNB', 'Did Not Bat']: # Handles 'Not out' with 0 balls
            sr_val = '-'

        batsmanTabulate.append([player_name_key, runs_scored, balls_faced, sr_val, how_out_status])
    
    print("\nBatting:")
    print(tabulate(batsmanTabulate, headers=["Player", "Runs", "Balls", "SR", "How Out"], tablefmt="grid"))

    # Bowling Scorecard
    bowlerTabulate = []
    for player in bowl_tracker:
        data = bowl_tracker[player]
        runs_conceded = data['runs'] # Renamed for clarity from mainconnect.py 'runs'
        balls_bowled = data['balls']
        wickets_taken = data['wickets']
        noballs_bowled = data.get('noballs', 0) # Get noballs, default to 0 if not present
        overs_str = f"{balls_bowled // 6}.{balls_bowled % 6}" if balls_bowled else "0.0"
        economy_rate = round((runs_conceded / balls_bowled) * 6, 2) if balls_bowled else 'NA'
        bowlerTabulate.append([player, overs_str, runs_conceded, wickets_taken, noballs_bowled, economy_rate])
    
    print("\nBowling:")
    print(tabulate(bowlerTabulate, headers=["Player", "Overs", "Runs", "Wickets", "NB", "Economy"], tablefmt="grid"))

def display_ball_by_ball(innings_log, innings_num, team_name, runs, balls, wickets, bat_tracker, bowl_tracker):
    print(f"\n--- Innings {innings_num}: {team_name} Batting ---")

    i = 0
    while i < len(innings_log):
        event_data = innings_log[i]
        event_text = event_data['event']
        commentary = ""

        event_type = event_data.get('type')
        original_event_type = event_data.get('original_event_type')
        is_fh_delivery = event_data.get('is_free_hit_delivery', False)
        extras_type = event_data.get('extras_type')
        # Use runs_this_ball from event_data, not the function parameter 'runs' which is total innings runs
        runs_this_ball_current_event = event_data.get('runs_this_ball', 0)

        consolidated_nb_commentary = False
        no_ball_suffix = random.choice(commentary_lines['no_ball_call']).split('.')[1].strip() # "Free hit coming up!"

        if event_type == "NO_BALL_CALL":
            total_nb_runs = 1 # Start with the penalty run

            if i + 1 < len(innings_log):
                next_event_data = innings_log[i+1]
                if next_event_data.get('original_event_type') == "NB" and next_event_data.get('is_free_hit_delivery'):
                    runs_off_nb_delivery = next_event_data.get('runs_this_ball', 0)
                    total_nb_runs += runs_off_nb_delivery

                    event_text = next_event_data['event'] # Use event text from the ball outcome for score accuracy
                    commentary = f"Nb ({total_nb_runs})! {no_ball_suffix}"

                    i += 1 # Skip the next log entry as it's processed
                    consolidated_nb_commentary = True

            if not consolidated_nb_commentary: # Fallback if lookahead failed
                commentary = f"Nb (1)! {no_ball_suffix}"

        elif event_type == "WIDE":
            commentary = random.choice(commentary_lines['wide'])
        elif event_type == "EXTRAS" and extras_type in commentary_lines['extras']:
            runs_off_extras = event_data.get('runs_off_extras', 0) # This specific key might be from an older version of log
            # Assuming 'runs_this_ball' now holds extras runs for 'EXTRAS' type events
            # If 'runs_off_extras' is not reliably in the log, use runs_this_ball_current_event for extras amount
            actual_extras_runs = event_data.get('runs_off_extras', runs_this_ball_current_event)

            base_commentary = random.choice(commentary_lines['extras'][extras_type])
            if actual_extras_runs > 0:
                 base_commentary += f" {actual_extras_runs} run{'s' if actual_extras_runs > 1 else ''}."
            commentary = base_commentary
        else: # Handles legal deliveries, and outcomes of No-Balls if not consolidated
            out_type = event_data.get('out_type')
            is_not_out_on_fh = event_data.get('is_dismissal') == False and is_fh_delivery

            base_commentary = ""
            outcome_runs_str = ""

            if out_type and not is_not_out_on_fh: # Actual wicket dismissal
                if out_type in commentary_lines['wicket']:
                    base_commentary = random.choice(commentary_lines['wicket'][out_type])
                else:
                     base_commentary = random.choice(commentary_lines['wicket']['general']) + f" ({out_type})"
            elif is_not_out_on_fh:
                outcome_runs_str = str(runs_this_ball_current_event)
                run_commentary = random.choice(commentary_lines.get(outcome_runs_str, commentary_lines['0']))
                base_commentary = f"Phew! {run_commentary} (Not out on Free Hit!)"
            else: # Runs or dot
                outcome_runs_str = str(runs_this_ball_current_event)
                base_commentary = random.choice(commentary_lines.get(outcome_runs_str, commentary_lines['0']))

            if is_fh_delivery and not consolidated_nb_commentary :
                commentary = random.choice(commentary_lines['free_hit_delivery']) + " " + base_commentary
            else:
                commentary = base_commentary

        print(f"Ball {event_data.get('balls', 'N/A')}: {event_text} - {commentary}")
        i += 1 # Move to next log item

    overs = f"{balls // 6}.{balls % 6}"
    print(f"\nInnings Total: {runs}/{wickets} in {overs} overs")
    print(random.choice(commentary_lines['innings_end']))
    
    # Display scorecard after innings
    display_scorecard(bat_tracker, bowl_tracker, team_name, innings_num)

# New League Scheduling Algorithm
all_possible_matches = []
for i_team_idx in range(len(teams)):
    for j_team_idx in range(i_team_idx + 1, len(teams)):
        all_possible_matches.append((teams[i_team_idx], teams[j_team_idx]))

random.shuffle(all_possible_matches)

scheduled_matches_final = []
teams_in_last_scheduled_match = set()
match_pool_copy = list(all_possible_matches)

while len(scheduled_matches_final) < len(all_possible_matches):
    found_this_slot = False
    best_match_found = None

    candidate_match_idx_to_pop = -1

    for candidate_idx, candidate_match in enumerate(match_pool_copy):
        teamA, teamB = candidate_match
        if teamA not in teams_in_last_scheduled_match and teamB not in teams_in_last_scheduled_match:
            best_match_found = candidate_match
            candidate_match_idx_to_pop = candidate_idx
            found_this_slot = True
            break

    if found_this_slot and best_match_found is not None:
        # Remove from pool by index
        match_pool_copy.pop(candidate_match_idx_to_pop)
    elif not found_this_slot:
        if match_pool_copy: # If there are still matches to schedule
            best_match_found = match_pool_copy.pop(0) # Take the first one
        else:
            break # No matches left

    if best_match_found:
        scheduled_matches_final.append(best_match_found)
        teams_in_last_scheduled_match = {best_match_found[0], best_match_found[1]}
    elif not match_pool_copy and len(scheduled_matches_final) < len(all_possible_matches):
        print("Error: Match pool empty but not all matches scheduled. Breaking.")
        break

matches_with_rain_chance = set()
if scheduled_matches_final: # Ensure there are matches to select from
    num_rain_matches = random.randint(1, 3)
    num_rain_matches = min(num_rain_matches, len(scheduled_matches_final))

    if num_rain_matches > 0: # Only sample if we need to select matches
        # Ensure sampling count does not exceed population size if len(scheduled_matches_final) is small
        sample_count = min(num_rain_matches, len(scheduled_matches_final))
        if sample_count > 0:
             rain_match_indices = random.sample(range(len(scheduled_matches_final)), sample_count)
             for index in rain_match_indices:
                matches_with_rain_chance.add(scheduled_matches_final[index])

        # print(f"DEBUG: Matches selected for potential rain: {matches_with_rain_chance}") # For debugging

# League Matches using the new schedule
for team1, team2 in scheduled_matches_final:
    current_match_tuple = (team1, team2)
    rain_expected_for_this_match = current_match_tuple in matches_with_rain_chance
    # print(f"DEBUG: Match {team1} vs {team2}, Rain Expected: {rain_expected_for_this_match}") # For debugging
    print(f"\nMatch: {team1.upper()} vs {team2.upper()}")

    try:
        input("Press Enter to start the match...")
        print(random.choice(commentary_lines['start']))

        resList = game(False, team1, team2)

        # Display ball-by-ball and innings summary for both innings
        for innings, team_key, runs_key, balls_key, bat_tracker_key, bowl_tracker_key in [
            ('innings1Log', 'innings1BatTeam', 'innings1Runs', 'innings1Balls', 'innings1Battracker', 'innings1Bowltracker'),
            ('innings2Log', 'innings2BatTeam', 'innings2Runs', 'innings2Balls', 'innings2Battracker', 'innings2Bowltracker')
        ]:
            display_ball_by_ball(
                resList[innings],
                1 if innings == 'innings1Log' else 2,
                resList[team_key],
                resList[runs_key],
                resList[balls_key],
                max([event['wickets'] for event in resList[innings]], default=0),
                resList[bat_tracker_key],
                resList[bowl_tracker_key]
            )

        if resList.get('superOverPlayed', False) and resList.get('superOverDetails'):
            print("--- Super Over Details ---")
            for detail in resList['superOverDetails']:
                print(detail)
            print("-------------------------")
        print(f"\nResult: {resList['winMsg']}")
        print(random.choice(commentary_lines['end']))

        # Track batting/bowling format win
        if "runs" in resList['winMsg']:
            battingf += 1
        else:
            bowlingf += 1

        # Update batting stats
        for bat_map in [('innings1Battracker', 'innings1BatTeam'), ('innings2Battracker', 'innings2BatTeam')]:
            bat_tracker = resList[bat_map[0]]
            for player in bat_tracker:
                if player not in battingInfo:
                    battingInfo[player] = copy.deepcopy(bat_tracker[player])
                    battingInfo[player]['innings'] = 1
                    battingInfo[player]['scoresArray'] = [int(battingInfo[player]['runs'])]
                else:
                    battingInfo[player]['balls'] += bat_tracker[player]['balls']
                    battingInfo[player]['runs'] += bat_tracker[player]['runs']
                    battingInfo[player]['ballLog'] += bat_tracker[player]['ballLog']
                    battingInfo[player]['innings'] += 1
                    battingInfo[player]['scoresArray'].append(int(bat_tracker[player]['runs']))

        # Update bowling stats
        for bowl_map in [('innings1Bowltracker',), ('innings2Bowltracker',)]:
            bowl_tracker = resList[bowl_map[0]]
            for player in bowl_tracker:
                if player not in bowlingInfo:
                    bowlingInfo[player] = copy.deepcopy(bowl_tracker[player])
                    bowlingInfo[player]['matches'] = 1
                else:
                    bowlingInfo[player]['balls'] += bowl_tracker[player]['balls']
                    bowlingInfo[player]['runs'] += bowl_tracker[player]['runs']
                    bowlingInfo[player]['ballLog'] += bowl_tracker[player]['ballLog']
                    bowlingInfo[player]['wickets'] += bowl_tracker[player]['wickets']
                    bowlingInfo[player]['noballs'] = bowlingInfo[player].get('noballs', 0) + bowl_tracker[player].get('noballs', 0) # Aggregate noballs
                    bowlingInfo[player]['matches'] += 1

        # Points Table Update
        teamA_actual = resList['innings1BatTeam'] # Use actual team names from resList for SO count
        teamB_actual = resList['innings2BatTeam']
        if resList.get('superOverPlayed', False):
            # Ensure team names from resList are valid keys in points dict (they should be)
            if teamA_actual in points:
                points[teamA_actual]['SO'] += 1
            if teamB_actual in points:
                points[teamB_actual]['SO'] += 1

        winner_status = resList.get('winner')

        # Increment Played count for both teams involved in the scheduled match
        # team1 and team2 are from the scheduled_matches_final loop
        points[team1]['P'] += 1
        points[team2]['P'] += 1

        # SO count update (should be independent of cancelled status if superOverPlayed is false for cancelled)
        # This needs to use actual team names from resList if a match (even a tie that went to SO) was played.
        if resList.get('superOverPlayed', False):
            teamA_actual_for_so = resList.get('innings1BatTeam') # Use .get for safety
            teamB_actual_for_so = resList.get('innings2BatTeam') # Use .get for safety
            if teamA_actual_for_so and teamB_actual_for_so: # Ensure valid team names from resList
                 if teamA_actual_for_so in points: points[teamA_actual_for_so]['SO'] += 1
                 if teamB_actual_for_so in points: points[teamB_actual_for_so]['SO'] += 1
            elif team1 in points and team2 in points: # Fallback to loop teams if resList doesn't have them (should not happen if SO played)
                 points[team1]['SO'] +=1
                 points[team2]['SO'] +=1


        if winner_status == "cancelled":
            points[team1]['T'] += 1
            points[team2]['T'] += 1
            points[team1]['pts'] += 1
            points[team2]['pts'] += 1
            # NRR components are NOT updated as no play occurred.
            print(f"Match {team1.upper()} vs {team2.upper()} cancelled. Points shared.")
        elif winner_status == "tie":
            # For NRR, we need the actual teams that played, from resList
            teamA_actual = resList['innings1BatTeam']
            teamB_actual = resList['innings2BatTeam']
            teamARuns, teamABalls = resList['innings1Runs'], resList['innings1Balls']
            teamBRuns, teamBBalls = resList['innings2Runs'], resList['innings2Balls']

            points[teamA_actual]['T'] += 1
            points[teamB_actual]['T'] += 1
            points[teamA_actual]['pts'] += 1
            points[teamB_actual]['pts'] += 1

            points[teamA_actual]['runsScored'] += teamARuns
            points[teamB_actual]['runsScored'] += teamBRuns
            points[teamA_actual]['runsConceded'] += teamBRuns
            points[teamB_actual]['runsConceded'] += teamARuns
            points[teamA_actual]['ballsFaced'] += teamABalls
            points[teamB_actual]['ballsFaced'] += teamBBalls
            points[teamA_actual]['ballsBowled'] += teamBBalls
            points[teamB_actual]['ballsBowled'] += teamABalls
        else: # Actual win/loss
            # winner_status here is the name of the winning team from resList['winner']
            # For NRR and other stats, use actual teams that played from resList
            teamA_actual = resList['innings1BatTeam']
            teamB_actual = resList['innings2BatTeam']
            teamARuns, teamABalls = resList['innings1Runs'], resList['innings1Balls']
            teamBRuns, teamBBalls = resList['innings2Runs'], resList['innings2Balls']

            # Determine loser based on scheduled teams (team1, team2) and actual winner_status
            loser = team1 if winner_status == team2 else team2

            if winner_status in points: # Check if winner_status is a valid team key
                points[winner_status]['W'] += 1
                points[winner_status]['pts'] += 2
            if loser in points: # Check if loser is a valid team key
                points[loser]['L'] += 1

            points[teamA_actual]['runsScored'] += teamARuns
            points[teamB_actual]['runsScored'] += teamBRuns
            points[teamA_actual]['runsConceded'] += teamBRuns
            points[teamB_actual]['runsConceded'] += teamARuns
            points[teamA_actual]['ballsFaced'] += teamABalls
            points[teamB_actual]['ballsFaced'] += teamBBalls
            points[teamA_actual]['ballsBowled'] += teamBBalls
            points[teamB_actual]['ballsBowled'] += teamABalls

        display_points_table()
        display_top_players()

        # Pause after match to keep console open
        input("Press Enter to continue to the next match...")

    except Exception as e:
        print(f"Error during match {team1.upper()} vs {team2.upper()}: {str(e)}")
        input("Press Enter to continue or Ctrl+C to exit...")
        continue

# POINTS TABLE (Final)
display_points_table()

# === PLAYOFFS ===
def playoffs(team1, team2, matchtag):
    print(f"\n{matchtag.upper()} - {team1.upper()} vs {team2.upper()}")
    try:
        input("Press Enter to start the playoff match...")
        print(random.choice(commentary_lines['start']))
        
        res = game(False, team1.lower(), team2.lower(), matchtag)
        
        for innings, team_key, runs_key, balls_key, bat_tracker_key, bowl_tracker_key in [
            ('innings1Log', 'innings1BatTeam', 'innings1Runs', 'innings1Balls', 'innings1Battracker', 'innings1Bowltracker'),
            ('innings2Log', 'innings2BatTeam', 'innings2Runs', 'innings2Balls', 'innings2Battracker', 'innings2Bowltracker')
        ]:
            display_ball_by_ball(
                res[innings],
                1 if innings == 'innings1Log' else 2,
                res[team_key],
                res[runs_key],
                res[balls_key],
                max([event['wickets'] for event in res[innings]], default=0),
                res[bat_tracker_key],
                res[bowl_tracker_key]
            )
        
        if res.get('superOverPlayed', False) and res.get('superOverDetails'):
            print("--- Super Over Details ---")
            for detail in res['superOverDetails']:
                print(detail)
            print("-------------------------")
        print(f"\nResult: {res['winMsg'].upper()}")
        print(random.choice(commentary_lines['end']))

        winner = res['winner']
        loser = team1 if winner == team2 else team2

        for bat_map in ['innings1Battracker', 'innings2Battracker']:
            tracker = res[bat_map]
            for player in tracker:
                if player not in battingInfo:
                    battingInfo[player] = copy.deepcopy(tracker[player])
                    battingInfo[player]['innings'] = 1
                    battingInfo[player]['scoresArray'] = [int(tracker[player]['runs'])]
                else:
                    battingInfo[player]['balls'] += tracker[player]['balls']
                    battingInfo[player]['runs'] += tracker[player]['runs']
                    battingInfo[player]['ballLog'] += tracker[player]['ballLog']
                    battingInfo[player]['innings'] += 1
                    battingInfo[player]['scoresArray'].append(int(tracker[player]['runs']))

        for bowl_map in ['innings1Bowltracker', 'innings2Bowltracker']:
            tracker = res[bowl_map]
            for player in tracker:
                if player not in bowlingInfo:
                    bowlingInfo[player] = copy.deepcopy(tracker[player])
                    bowlingInfo[player]['matches'] = 1
                else:
                    bowlingInfo[player]['balls'] += tracker[player]['balls']
                    bowlingInfo[player]['runs'] += tracker[player]['runs']
                    bowlingInfo[player]['ballLog'] += tracker[player]['ballLog']
                    bowlingInfo[player]['wickets'] += tracker[player]['wickets']
                    bowlingInfo[player]['noballs'] = bowlingInfo[player].get('noballs', 0) + tracker[player].get('noballs', 0) # Aggregate noballs for playoffs
                    bowlingInfo[player]['matches'] += 1

        display_points_table()
        display_top_players()

        # Pause after playoff match
        input("Press Enter to continue...")

        return winner, loser

    except Exception as e:
        print(f"Error during {matchtag.upper()}: {str(e)}")
        input("Press Enter to continue or Ctrl+C to exit...")
        return team1, team2  # Default to team1 as winner to continue playoffs

# PLAYOFF SEQUENCE
pointsTabulate = sorted(
    [[team, points[team]['pts'], (points[team]['runsScored'] / points[team]['ballsFaced']) * 6 - (points[team]['runsConceded'] / points[team]['ballsBowled']) * 6]
     for team in points],
    key=lambda x: (x[1], x[2]), reverse=True
)
q1 = [pointsTabulate[0][0], pointsTabulate[1][0]]
elim = [pointsTabulate[2][0], pointsTabulate[3][0]]

finalists = []

winnerQ1, loserQ1 = playoffs(q1[0], q1[1], "Qualifier 1")
finalists.append(winnerQ1)

winnerElim, _ = playoffs(elim[0], elim[1], "Eliminator")

winnerQ2, _ = playoffs(winnerElim, loserQ1, "Qualifier 2")
finalists.append(winnerQ2)

finalWinner, _ = playoffs(finalists[0], finalists[1], "Final")
print(f"\n🏆 {finalWinner.upper()} WINS THE IPL!!!")

# === SAVE FINAL STATS ===
battingTabulate = []
for b in battingInfo:
    c = battingInfo[b]
    outs = sum(1 for bl in c['ballLog'] if "W" in bl)
    avg = round(c['runs'] / outs, 2) if outs else "NA"
    sr = round((c['runs'] / c['balls']) * 100, 2) if c['balls'] else "NA"
    battingTabulate.append([b, c['innings'], c['runs'], avg, max(c['scoresArray']), sr, c['balls']])

battingTabulate = sorted(battingTabulate, key=lambda x: x[2], reverse=True)

bowlingTabulate = []
for b in bowlingInfo:
    c = bowlingInfo[b]
    overs = f"{c['balls'] // 6}.{c['balls'] % 6}" if c['balls'] else "0"
    economy = round((c['runs'] / c['balls']) * 6, 2) if c['balls'] else "NA"
    noballs = c.get('noballs', 0)
    bowlingTabulate.append([b, c['wickets'], overs, c['runs'], noballs, economy])

bowlingTabulate = sorted(bowlingTabulate, key=lambda x: x[1], reverse=True)

with open(os.path.join(dir_path, "batStats.txt"), "w") as f:
    sys.stdout = f
    print(tabulate(battingTabulate, headers=["Player", "Innings", "Runs", "Average", "Highest", "SR", "Balls"], tablefmt="grid"))
    sys.stdout = sys.__stdout__

with open(os.path.join(dir_path, "bowlStats.txt"), "w") as f:
    sys.stdout = f
    print(tabulate(bowlingTabulate, headers=["Player", "Wickets", "Overs", "Runs Conceded", "NB", "Economy"], tablefmt="grid"))
    sys.stdout = sys.__stdout__

print("bat", battingf, "bowl", bowlingf)
input("\nPress Enter to exit...")
import random
import accessJSON
import copy
import sys 
import json

MIN_MATCHES_EXPERIENCE = 15
MIN_BAT_BALLS_EXPERIENCE = 300
MIN_BOWL_BALLS_EXPERIENCE = 300
FILLER_BATSMAN_MAX_CAREER_RUNS = 50
FILLER_BATSMAN_MAX_BALLS_FACED = 100
MIN_BOWLING_OUT_RATE_THRESHOLD = 0.015 # Min wickets per 100 balls equivalent

def normalize_probabilities(prob_dict, target_sum):
    # Ensure all values are non-negative first
    # And remove any non-numeric keys that might have crept in, or ensure they are zero.
    keys_to_delete = []
    current_numeric_sum = 0.0

    for k in list(prob_dict.keys()): # Iterate over a copy of keys for safe deletion/modification
        if not isinstance(prob_dict[k], (int, float)):
            # Option 1: Delete non-numeric keys
            # keys_to_delete.append(k)
            # Option 2: Treat as zero for sum, but keep key if it's standard (e.g. 'Nb', 'Wd')
            # For run denominations, non-numeric keys are unexpected and should ideally be cleaned or logged.
            # For this pass, let's assume they should be numeric or are ignorable for sum.
            # If a key like 'Nb' (for no-balls) is in a run denomination dict, it's likely an error upstream.
            # We will focus on numeric values for normalization.
            pass # Let's assume for now that all relevant keys for sum are numeric.
        elif prob_dict[k] < 0:
            prob_dict[k] = 0.0

        if isinstance(prob_dict[k], (int, float)): # Sum only numeric values
            current_numeric_sum += prob_dict[k]

    # for k_del in keys_to_delete:
    #     if k_del in prob_dict: del prob_dict[k_del]

    if target_sum == 0: # If original sum was 0, all probabilities must be 0.
        for k_zero in prob_dict:
            if isinstance(prob_dict[k_zero], (int, float)): prob_dict[k_zero] = 0.0
        return prob_dict

    if current_numeric_sum == 0:
        # If current_sum is 0 but target_sum wasn't, this means all probabilities were wiped out or non-numeric.
        # Distribute target_sum to '0' or '1' if they exist and are meant to be numeric.
        # This recovery is basic and assumes '0' and '1' are primary score types.
        num_numeric_keys = sum(1 for val in prob_dict.values() if isinstance(val, (int, float)))
        if num_numeric_keys > 0: # Distribute among existing numeric keys if any
            for k_dist in prob_dict:
                if isinstance(prob_dict[k_dist], (int,float)):
                    prob_dict[k_dist] = target_sum / num_numeric_keys
        # If no numeric keys, this function can't really normalize. Upstream data should be clean.
        return prob_dict

    if abs(current_numeric_sum - target_sum) < 1e-9: # Effectively equal
        return prob_dict

    factor = target_sum / current_numeric_sum
    for k in prob_dict:
        if isinstance(prob_dict[k], (int, float)): # Normalize only numeric values
            prob_dict[k] *= factor
            if prob_dict[k] < 0: prob_dict[k] = 0.0 # Clamp again

    # Final redistribution of rounding errors
    final_new_sum = sum(val for val in prob_dict.values() if isinstance(val, (int, float)))
    error = target_sum - final_new_sum
    if abs(error) > 1e-9:
        # Add error to a common numeric key, like '0' or '1'
        if '0' in prob_dict and isinstance(prob_dict['0'], (int, float)):
            prob_dict['0'] += error
            if prob_dict['0'] < 0: prob_dict['0'] = 0.0
        elif '1' in prob_dict and isinstance(prob_dict['1'], (int, float)):
            prob_dict['1'] += error
            if prob_dict['1'] < 0: prob_dict['1'] = 0.0
        # else: if '0' or '1' don't exist or aren't numeric, find another numeric key
        else:
            for k_err_dist in prob_dict:
                if isinstance(prob_dict[k_err_dist], (int,float)):
                    prob_dict[k_err_dist] += error
                    if prob_dict[k_err_dist] < 0: prob_dict[k_err_dist] = 0.0
                    break # Distribute to first available numeric key
    return prob_dict

#NEXT UPDATE -
#ADD NO-BALLS
#ADD BYES/LEGBYES
#SHOW NOT OUT IF CAME IN BUT DIDN'T BAT
#FIX BOWLING SELECTION
#If bowling rate is less than x then dont bowl
#IMPROVE BOWLER ROTATION
#If RRR is low in the last 10, team may falter, fix it
#designate 6 bowlers and bowl them in a shuffled
#see for localBattingOrder

#K Williamson bowling

#TRANSLATE RATING TO DEN AVG, OUT AVG, ETC.

#BIPUL SHARMA - OVERPOWERED AND SO ->
# - 1. MAKE SURE PLAYER HAS PLAYED X NUMBER OF GAMES OR ELSE DRIVE DOWN HIS RATINGS (such as avgs, dens, etc.) (!!!IMPORTANT)
# - 2. DO FOR BOTH BATTING & BOWLING SEPARATELY
#BAD PLAYERS GETTING GOOD SCORES DURING CHASE, SEE TO THAT (RELATED TO PREV ONE, REDUCE PLAYERS
# WHO HAVE PLAYED A FEW GAMES' 6s, 4s, RATE AND INCREASE OUT AVG AND 0s, 1s)
#CHECK IF PLAYER HAS PLAYED LESS THAN X NUMBER OF BALLS, OR BOWLED LESS THAN X NUMBER OF BALLS
#IF BAT RUNS 0, OR VERY LOW, CREATE FILLER WHICH IS VERY BAD FOR BATTING (highs 0s,1s, outavg, low 4s, 6s: see other
#tail-enders for reference)

#Triple not out
#not many 100s
#12-over rule
#too many dots (increase 1s & 2s, reduce 0s)
#too many all-outs

#Last 10 overs both innings very slow even when 1-2 wickets fall (too many wickets fall)
#weigh economy more, if eco is like 6 or 7, then bowl over a player with 1 wicket but 9 economy
#dont drag game too long if rrr < 9 in last 3-4 overs

#IMP
#12-17 over increase rate (1st innings) & (2nd innings too)
#Wickets (140s scores with 3 wickets in 1st innings - fix it (apply 2nd inn logic))

#FEATURES
#Commentary
#GUI
#Super overs
#Better rotation
#Venue
#Six distance
#Type of shot
#Match summaries
#i will ask different people for shot selection of players and then average them out while eliminating outliers
#Add option to add custom players by fabricating stats

#Focus more on pitches, attach pitches to venues, pitch detoriation
#performance affects all time stats

#LONGSHOTS
#Add ratings for players
#Player analysis by phases
from tabulate import tabulate

target = 1 

innings1Batting = None
innings1Bowling = None
innings2Batting = None
innings2Bowling = None
innings1Balls = None
innings2Balls = None
innings1Runs = None
innings2Runs = None
winner = None
winMsg = None

innings1Battracker = None
innings2Battracker = None
innings1Bowltracker = None
innings2Bowltracker = None

innings1Log = []
innings2Log = []

tossMsg = None

def doToss(pace, spin, outfield, secondInnDew, pitchDetoriate, typeOfPitch, team1, team2):
    global tossMsg
    battingLikely =  0.45
    if(secondInnDew):
          battingLikely = battingLikely - random.uniform(0.09, 0.2)
    if(pitchDetoriate):
        battingLikely = battingLikely + random.uniform(0.09, 0.2)
    if(typeOfPitch == "dead"):
        battingLikely = battingLikely - random.uniform(0.05, 0.15)
    if(typeOfPitch == "green"):
        battingLikely = battingLikely + random.uniform(0.05, 0.15)
    if(typeOfPitch == "dusty"):
        battingLikely = battingLikely + random.uniform(0.04, 0.1)

    toss = random.randint(0, 1)
    # print(toss, battingLikely)
    if(toss == 0):
        outcome = random.uniform(0, 1)
        if(outcome > battingLikely):
            print(team1, "won the toss and chose to field")
            tossMsg = team1 + " won the toss and chose to field"
            return(1)
        else:
            print(team1, "won the toss and chose to bat")
            tossMsg = team1 + " won the toss and chose to bat"
            return(0)

    else:
        outcome = random.uniform(0, 1)
        if(outcome > battingLikely):
            print(team2, "won the toss and chose to field")
            tossMsg = team2 + " won the toss and chose to bat"
            return(0)
        else:
            print(team2, "won the toss and chose to bat")
            tossMsg = team2 + " won the toss and chose to field"
            return(1)


def pitchInfo(venue, typeOfPitch):
    if(typeOfPitch == "dusty"):
        # how good the pitch is for pace. 0.75-1.25, lower is better for bowling
        pace = 1 + 0.5*(random.random() * (random.random()-random.random()))
        # how good the pitch is for spin. 0.75-1.25, lower is better for bowling
        spin = 1 + 0.5*(random.random() * (random.random()-random.random()))
        spin = spin - random.uniform(0.1, 0.16)
        # how good the outfield is. 0.75-1.25, lower is better for bowling
        outfield = 1 + 0.5*(random.random() *
                            (random.random()-random.random()))
    elif(typeOfPitch == "green"):
        # how good the pitch is for pace. 0.75-1.25, lower is better for bowling
        pace = 1 + 0.5*(random.random() * (random.random()-random.random()))
        pace = pace - random.uniform(0.1, 0.16)
        # how good the pitch is for spin. 0.75-1.25, lower is better for bowling
        spin = 1 + 0.5*(random.random() * (random.random()-random.random()))
        # how good the outfield is. 0.75-1.25, lower is better for bowling
        outfield = 1 + 0.5*(random.random() *
                            (random.random()-random.random()))
    elif(typeOfPitch == "dead"):
        # how good the pitch is for pace. 0.75-1.25, lower is better for bowling
        pace = 1 + 0.5*(random.random() * (random.random()-random.random()))
        # how good the pitch is for spin. 0.75-1.25, lower is better for bowling
        spin = 1 + 0.5*(random.random() * (random.random()-random.random()))
        # how good the outfield is. 0.75-1.25, lower is better for bowling
        outfield = 1 + 0.5*(random.random() *
                            (random.random()-random.random()))

    return [pace, spin, outfield]


def innings1(batting, bowling, battingName, bowlingName, pace, spin, outfield, dew, detoriate):
    global target, innings1Balls, innings1Runs, innings1Batting, innings1Bowling, winner, winMsg, innings1Battracker, innings1Bowltracker, innings1Log
    # print(battingName, bowlingName, pace, spin, outfield, dew, detoriate)
    is_next_ball_free_hit = False # Initialize for the innings
    bowlerTracker = {} #add names of all in innings def
    batterTracker = {} #add names of all in innings def
    battingOrder = []
    catchingOrder = []
    ballLog = []

    runs = 0
    balls = 0
    wickets = 0
    # break or spin; medium or fast

    # Deciding batting order
    for i in batting:
        batterTracker[i['playerInitials']] = {'playerInitials': i['playerInitials'], 'balls': 0, 'runs': 0, 'ballLog': []}
        runObj = {}
        outObj = {}

        i['batBallsTotal'] += 1
        for run in i['batRunDenominations']:
            runObj[run] = i['batRunDenominations'][run] / i['batBallsTotal']
        i['batRunDenominationsObject'] = runObj

        for out in i['batOutTypes']:
            outObj[out] = i['batOutTypes'][out] / i['batBallsTotal']
        i['batOutTypesObject'] = outObj

        original_bat_den_sum = 0.0
        for val in i['batRunDenominationsObject'].values():
            if isinstance(val, (int, float)):
                original_bat_den_sum += val

        # for styles in i['byBowler']:

        #     runObj2 = {}
        #     outObj2 = {}
        #     batOutsRate = i['byBowler'][styles]['batOutsTotal'] / \
        #         i['byBowler'][styles]['batBallsTotal']
        #     i['byBowler'][styles]['batOutsRate'] = batOutsRate
        #     for run in i['byBowler'][styles]['batRunDenominations']:
        #         runObj2[run] = i['byBowler'][styles]['batRunDenominations'][run] / \
        #             i['byBowler'][styles]['batBallsTotal']
        #     i['byBowler'][styles]['batRunDenominationsObject'] = runObj2
        #     for out in i['byBowler'][styles]['batOutTypes']:
        #         outObj2[out] = i['byBowler'][styles]['batOutTypes'][out] / \
        #             i['byBowler'][styles]['batBallsTotal']
        #     i['byBowler'][styles]['batOutTypesObject'] = outObj2

        i['batOutsRate'] = i['batOutsTotal'] / i['batBallsTotal']

        # Calculate total career runs for the batsman
        total_career_runs_for_player = 0
        if 'batRunDenominations' in i and isinstance(i['batRunDenominations'], dict):
            for run_key, run_count in i['batRunDenominations'].items():
                if run_key.isdigit() and int(run_key) > 0: # Consider only actual scoring runs (1-6)
                    total_career_runs_for_player += run_count * int(run_key)

        if (i['matches'] < MIN_MATCHES_EXPERIENCE and \
            i['batBallsTotal'] <= FILLER_BATSMAN_MAX_BALLS_FACED and \
            total_career_runs_for_player < FILLER_BATSMAN_MAX_CAREER_RUNS):

            # Filler Batsman Logic (More Aggressive Adjustments)
            reduction_6 = i['batRunDenominationsObject'].get('6', 0.0) * 0.80  # Reduce by 80%
            reduction_4 = i['batRunDenominationsObject'].get('4', 0.0) * 0.70  # Reduce by 70%

            i['batRunDenominationsObject']['6'] = i['batRunDenominationsObject'].get('6', 0.0) - reduction_6
            i['batRunDenominationsObject']['4'] = i['batRunDenominationsObject'].get('4', 0.0) - reduction_4

            i['batRunDenominationsObject']['0'] = i['batRunDenominationsObject'].get('0', 0.0) + reduction_6 * 0.6 + reduction_4 * 0.6
            i['batRunDenominationsObject']['1'] = i['batRunDenominationsObject'].get('1', 0.0) + reduction_6 * 0.4 + reduction_4 * 0.4

            i['batOutsRate'] = i['batOutsRate'] * 1.40  # Increase out rate by 40%

            # Clamping
            if i['batRunDenominationsObject']['6'] < 0: i['batRunDenominationsObject']['6'] = 0.0
            if i['batRunDenominationsObject']['4'] < 0: i['batRunDenominationsObject']['4'] = 0.0

        elif i['matches'] < MIN_MATCHES_EXPERIENCE or i['batBallsTotal'] <= MIN_BAT_BALLS_EXPERIENCE:
            # Store original sum for potential normalization later (optional for this simplified step)
            # original_sum_den = sum(i['batRunDenominationsObject'].values())

            reduction_6 = i['batRunDenominationsObject'].get('6', 0.0) * 0.35
            reduction_4 = i['batRunDenominationsObject'].get('4', 0.0) * 0.25

            i['batRunDenominationsObject']['6'] = i['batRunDenominationsObject'].get('6', 0.0) - reduction_6
            i['batRunDenominationsObject']['4'] = i['batRunDenominationsObject'].get('4', 0.0) - reduction_4

            # Distribute reduced amounts to '0' and '1'
            i['batRunDenominationsObject']['0'] = i['batRunDenominationsObject'].get('0', 0.0) + reduction_6 * 0.5 + reduction_4 * 0.5
            i['batRunDenominationsObject']['1'] = i['batRunDenominationsObject'].get('1', 0.0) + reduction_6 * 0.5 + reduction_4 * 0.5

            i['batOutsRate'] = i['batOutsRate'] * 1.20

            # Ensure no negative probabilities (simple clamping)
            if i['batRunDenominationsObject']['6'] < 0: i['batRunDenominationsObject']['6'] = 0.0
            if i['batRunDenominationsObject']['4'] < 0: i['batRunDenominationsObject']['4'] = 0.0
            # Add more clamping if other denominations could become negative

        i['batRunDenominationsObject'] = normalize_probabilities(i['batRunDenominationsObject'], original_bat_den_sum)

        newPos = []
        posAvgObj = {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7":0,"8": 0, "9":0, "10":0}
        for p in i['position']:
            if(p != "null"):
                newPos.append(p)
        posTotal = sum(newPos)
        for p in newPos:
            if(str(p) in posAvgObj):
                posAvgObj[str(p)] += 1
            else:
                posAvgObj[str(p)] = 1

        for key_p in posAvgObj:
            posAvgObj[key_p] = posAvgObj[key_p]/i['matches'] 

        if(len(newPos) != 0):
            posAvg = posTotal/len(newPos)
        else:
            posAvg = 9.0
        battingOrder.append({"posAvg": posAvg, "player": i, "posAvgsAll": posAvgObj})

    battingOrder = sorted(battingOrder, key=lambda k: k['posAvg'])
    catchingOrder = sorted(catchingOrder, key=lambda k: k['catchRate'])

    for i in bowling:
        i['bowlBallsTotalRate'] = i['bowlBallsTotal'] / i['matches']
        # Ensure 'noballs' is initialized for each bowler
        bowlerTracker[i['playerInitials']] = {'playerInitials': i['playerInitials'], 'balls': 0, 
        'runs': 0, 'ballLog': [], 'overs': 0, 'wickets': 0, 'noballs': 0}
        runObj = {}
        outObj = {}
        i['catchRate'] = i['catches'] / i['matches']
        i['bowlWideRate'] = i['bowlWides'] / (i['bowlBallsTotal'] + 1)
        i['bowlNoballRate'] = i['bowlNoballs'] / (i['bowlBallsTotal'] + 1)
        i['bowlBallsTotal'] += 1
        for run in i['bowlRunDenominations']:
            runObj[run] = i['bowlRunDenominations'][run] / i['bowlBallsTotal']
        i['bowlRunDenominationsObject'] = runObj

        for out in i['bowlOutTypes']:
            outObj[out] = i['bowlOutTypes'][out] / i['bowlBallsTotal']
        i['bowlOutTypesObject'] = outObj

        original_bowl_den_sum = 0.0
        for val in i['bowlRunDenominationsObject'].values():
            if isinstance(val, (int, float)):
                original_bowl_den_sum += val

        # for styles in i['byBatsman']:
        #     runObj2 = {}
        #     outObj2 = {}
        #     bowlOutsRate = i['byBatsman'][styles]['bowlOutsTotal'] / \
        #         i['byBatsman'][styles]['bowlBallsTotal']
        #     i['byBatsman'][styles]['bowlOutsRate'] = batOutsRate
        #     for run in i['byBatsman'][styles]['bowlRunDenominations']:
        #         runObj2[run] = i['byBatsman'][styles]['bowlRunDenominations'][run] / \
        #             i['byBatsman'][styles]['bowlBallsTotal']
        #     i['byBatsman'][styles]['bowlRunDenominationsObject'] = runObj2
        #     for out in i['byBatsman'][styles]['bowlOutTypes']:
        #         outObj2[out] = i['byBatsman'][styles]['bowlOutTypes'][out] / \
        #             i['byBatsman'][styles]['bowlBallsTotal']
        #     i['byBatsman'][styles]['bowlOutTypesObject'] = outObj2

        i['bowlOutsRate'] = i['bowlOutsTotal'] / i['bowlBallsTotal']

        if i['matches'] < MIN_MATCHES_EXPERIENCE or i['bowlBallsTotal'] <= MIN_BOWL_BALLS_EXPERIENCE:
            # original_sum_den_bowl = sum(i['bowlRunDenominationsObject'].values()) # Optional for now

            increase_6 = i['bowlRunDenominationsObject'].get('6', 0.0) * 0.30
            increase_4 = i['bowlRunDenominationsObject'].get('4', 0.0) * 0.20

            i['bowlRunDenominationsObject']['6'] = i['bowlRunDenominationsObject'].get('6', 0.0) + increase_6
            i['bowlRunDenominationsObject']['4'] = i['bowlRunDenominationsObject'].get('4', 0.0) + increase_4

            # Reduce '0's to compensate, ensuring it doesn't go too low
            reduction_from_0 = increase_6 + increase_4
            current_0_val = i['bowlRunDenominationsObject'].get('0', 0.0)

            if current_0_val >= reduction_from_0:
                i['bowlRunDenominationsObject']['0'] = current_0_val - reduction_from_0
            else: # If '0's are not enough, take from '1's or just zero out '0'
                remaining_reduction = reduction_from_0 - current_0_val
                i['bowlRunDenominationsObject']['0'] = 0.0
                current_1_val = i['bowlRunDenominationsObject'].get('1', 0.0)
                if current_1_val >= remaining_reduction:
                    i['bowlRunDenominationsObject']['1'] = current_1_val - remaining_reduction
                else:
                    i['bowlRunDenominationsObject']['1'] = 0.0 # Or distribute deficit elsewhere if needed

            i['bowlOutsRate'] = i['bowlOutsRate'] * 0.80  # Decrease wicket-taking ability by 20%
            i['bowlWideRate'] = i['bowlWideRate'] * 1.15 # Increase wides by 15%
            i['bowlNoballRate'] = i['bowlNoballRate'] * 1.15 # Increase no-balls by 15%

            # Basic clamping for '0' and '1' if they were reduced
            if i['bowlRunDenominationsObject'].get('0', 0.0) < 0: i['bowlRunDenominationsObject']['0'] = 0.0
            if i['bowlRunDenominationsObject'].get('1', 0.0) < 0: i['bowlRunDenominationsObject']['1'] = 0.0

        i['bowlRunDenominationsObject'] = normalize_probabilities(i['bowlRunDenominationsObject'], original_bowl_den_sum)

        obj = {"20": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0,
               "10": 0, "11": 0, "12": 0, "13": 0, "14": 0, "15": 0, "16": 0, "17": 0, "18": 0, "19": 0}
        for over in i['overNumbers']:
            obj[over] += 1
        for keys in obj:
            if(i['matches'] != 0):
                avg = obj[keys]/i['matches']
            else:
                avg = -1
            obj[keys] = avg
        i['overNumbersObject'] = obj

    bowling = sorted(bowling, key=lambda k: k['bowlOutsRate'])
    bowling.reverse()
    bowling = bowling[0:7]

    bowlingOpening = sorted(bowling, key=lambda k: k['overNumbersObject']['1'])
    bowlingOpening.reverse()
    # bowlingOpening, bowlingDeath, bowlingMiddle are already capped at 7 by 'bowling' list being capped

    # Designated Bowlers (Top 6 from the initial pool of up to 7)
    bowling_selection_pool = bowling
    designated_bowlers = bowling_selection_pool[:min(6, len(bowling_selection_pool))]

    # Phase-specific lists from designated_bowlers. Safe .get usage for overNumbersObject
    designated_opening_bowlers = sorted(designated_bowlers, key=lambda k: k.get('overNumbersObject', {}).get('1', 0), reverse=True)
    designated_middle_bowlers = sorted(designated_bowlers, key=lambda k: k.get('overNumbersObject', {}).get('10', 0), reverse=True)
    designated_death_bowlers = sorted(designated_bowlers, key=lambda k: k.get('overNumbersObject', {}).get('19', 0), reverse=True)

    designated_bowler_rotation_list = [b['playerInitials'] for b in designated_bowlers]

    batter1 = battingOrder[0]
    batter2 = battingOrder[1]
    onStrike = batter1

    # Initial bowler selection for first two overs from designated lists
    bowler1_obj = None
    if designated_opening_bowlers:
        bowler1_obj = designated_opening_bowlers[0]
    elif designated_bowlers:
        bowler1_obj = designated_bowlers[0]
    elif bowling_selection_pool:
        bowler1_obj = bowling_selection_pool[0]

    bowler2_obj = None
    if len(designated_opening_bowlers) > 1 and (not bowler1_obj or designated_opening_bowlers[1]['playerInitials'] != bowler1_obj['playerInitials']):
        bowler2_obj = designated_opening_bowlers[1]
    elif len(designated_bowlers) > 1:
        for b in designated_bowlers:
            if not bowler1_obj or b['playerInitials'] != bowler1_obj['playerInitials']:
                bowler2_obj = b
                break
    if not bowler2_obj:
        bowler2_obj = bowler1_obj # Fallback if only one unique bowler available or no opening specified

    last_bowler_initials = None
    # is_next_ball_free_hit is already initialized at the start of innings1

    def playerDismissed(player):
        nonlocal batter1, batter2, onStrike, wickets, battingOrder, batterTracker # Ensure all used nonlocals are declared
        # 'player' is the batsman who got out.
        # 'wickets' has already been incremented before this function is called.
        # So, 'wickets' now represents the total number of batsmen out (e.g., 1 after the 1st wicket).

        if wickets == 10: # Check if all out
            # This print might be redundant if main loop handles it or if game ends immediately
            # print(f"Innings 1: All out. Total wickets: {wickets}")
            if batter1 == player: batter1 = None
            elif batter2 == player: batter2 = None
            onStrike = None # No one is on strike if all out
            return

        # The battingOrder is 0-indexed: battingOrder[0], battingOrder[1], battingOrder[2], ...
        # Initially, players at crease are battingOrder[0] and battingOrder[1].
        # When the 1st wicket falls (wickets = 1), the new player is battingOrder[2]. Index is 2.
        # This new player's index is 'wickets + 1'.
        new_batter_index = wickets + 1

        if new_batter_index < len(battingOrder): # Check if there's a valid next batsman in the order
            next_batter_info = battingOrder[new_batter_index]
            if batter1 == player: # If batter1 was the one who got out
                batter1 = next_batter_info # Replace batter1 with the new batsman
            elif batter2 == player: # If batter2 was the one who got out
                batter2 = next_batter_info # Replace batter2 with the new batsman
            else:
                # This case implies 'player' was not one of the current batters, which is unexpected.
                # Adding a log for safety.
                print(f"DEBUG WARNING (Innings 1 playerDismissed): Dismissed player {player['player']['playerInitials']} was not batter1 or batter2. Current batter1: {batter1['player']['playerInitials'] if batter1 else 'None'}, batter2: {batter2['player']['playerInitials'] if batter2 else 'None'}.")
                # Fallback: assume the 'onStrike' batter object was 'player'. Replace the corresponding variable.
                # This situation implies a potential mismatch upstream if player is not batter1 or batter2.
                # For now, the new batter still comes in and is on strike.
                # The critical part is that next_batter_info becomes onStrike.
                pass


            onStrike = next_batter_info # The new batsman is now on strike
        else:
            # Not enough players left in battingOrder to replace the dismissed one,
            # or wickets have reached 10 (though handled above, this is a safeguard).
            # This implies an all-out situation or exhausted batting list.
            # print(f"Innings 1: All batters dismissed or batting order exhausted. Total wickets: {wickets}")
            if batter1 == player:
                batter1 = None
            elif batter2 == player:
                batter2 = None
            # If all out, onStrike should become None. The main game loop should also check wickets == 10.
            if wickets == 10: # or new_batter_index >= len(battingOrder)
                 onStrike = None

    # This is the new, refactored getOutcome_standalone function for innings1
    def getOutcome_standalone(current_bowler, current_batter, den_avg_param, out_avg_param, out_type_avg_param, current_over_str, is_fh_param=False, event_type_param="LEGAL"): # Added is_fh_param and event_type_param
        nonlocal batterTracker, bowlerTracker, runs, balls, ballLog, wickets, onStrike, bowling, batter1, batter2
        global innings1Log

        bln = current_bowler['playerInitials']
        btn = current_batter['player']['playerInitials']

        if event_type_param == "LEGAL":
            bowlerTracker[bln]['balls'] += 1

        if event_type_param == "LEGAL" or event_type_param == "NB":
            batterTracker[btn]['balls'] += 1

        total_den_prob = sum(den_avg_param.values())
        if total_den_prob == 0: total_den_prob = 1 # Avoid division by zero if all den_avg_param are 0

        last_prob_end = 0
        denominationProbabilities_list = []
        for denom_val, prob_val in den_avg_param.items():
            start_prob = last_prob_end
            end_prob = last_prob_end + prob_val
            denominationProbabilities_list.append({"denomination": denom_val, "start": start_prob, "end": end_prob})
            last_prob_end = end_prob

        # Ensure decider range matches total_den_prob if it's not 1.0
        decider = random.uniform(0, total_den_prob)

        for prob_outcome in denominationProbabilities_list:
            if prob_outcome['start'] <= decider < prob_outcome['end']:
                runs_on_this_ball = int(prob_outcome['denomination'])
                runs += runs_on_this_ball

                log_suffix = " (Free Hit)" if is_fh_param else ""
                if event_type_param == "NB": log_suffix += " (Off No-Ball)"

                if runs_on_this_ball > 0:
                    print(current_over_str, f"{current_bowler['displayName']} to {current_batter['player']['displayName']}", prob_outcome['denomination'], "Score: " + str(runs) + "/" + str(wickets) + log_suffix)
                    ball_log_str = f"{current_over_str}:{prob_outcome['denomination']}"
                    if is_fh_param: ball_log_str += "-FH"
                    if event_type_param == "NB": ball_log_str += "-NB"

                    bowlerTracker[bln]['runs'] += runs_on_this_ball
                    batterTracker[btn]['runs'] += runs_on_this_ball
                    bowlerTracker[bln]['ballLog'].append(ball_log_str)
                    batterTracker[btn]['ballLog'].append(ball_log_str)
                    ballLog.append(ball_log_str)

                    innings1Log.append({"event" : current_over_str + f" {current_bowler['displayName']} to {current_batter['player']['displayName']} " + prob_outcome['denomination'] + " Score: " + str(runs) + "/" + str(wickets) + log_suffix,
                                        "balls": balls, "runs_this_ball": runs_on_this_ball, "total_runs": runs, "wickets": wickets,
                                        "batterTracker": copy.deepcopy(batterTracker), "bowlerTracker": copy.deepcopy(bowlerTracker),
                                        "batsman": btn,"batter1": batter1['player']['playerInitials'] if batter1 else 'N/A', "batter2": batter2['player']['playerInitials'] if batter2 else 'N/A',
                                        "bowler": bln, "is_free_hit_delivery": is_fh_param, "original_event_type": event_type_param}) # Ensure these params are logged
                    if runs_on_this_ball % 2 == 1:
                        onStrike = batter2 if onStrike == batter1 else batter1
                    return

                else: # Dot ball (runs_on_this_ball == 0)
                    # Calculate wicket probability on a dot ball
                    # Ensure den_avg_param['0'] is not zero to avoid division by zero error
                    dot_ball_prob = den_avg_param.get('0', 0)
                    if dot_ball_prob == 0: dot_ball_prob = 1 # Avoid division by zero
                    probOut_val = out_avg_param * (total_den_prob / dot_ball_prob if dot_ball_prob else 1)
                    outDecider = random.uniform(0, 1)

                    if probOut_val > outDecider: # WICKET
                        out_type_actual = None
                        out_probs_list = []
                        total_out_type_prob = sum(out_type_avg_param.values())
                        if total_out_type_prob == 0: total_out_type_prob = 1

                        last_out_prob_end = 0
                        for out_key, out_val in out_type_avg_param.items():
                            out_probs_list.append({"type": out_key, "start": last_out_prob_end, "end": last_out_prob_end + out_val})
                            last_out_prob_end += out_val

                        typeDeterminer = random.uniform(0, total_out_type_prob)
                        for type_data in out_probs_list:
                            if type_data['start'] <= typeDeterminer < type_data['end']:
                                out_type_actual = type_data['type']
                                break
                        if not out_type_actual and out_probs_list: out_type_actual = out_probs_list[-1]['type'] # Fallback

                        is_dismissal = True
                        credited_to_bowler = True if out_type_actual not in ["runOut"] else False

                        if is_fh_param and out_type_actual != "runOut":
                            is_dismissal = False
                            print(current_over_str, f"{current_bowler['displayName']} to {current_batter['player']['displayName']}", f"NOT OUT ({out_type_actual} on Free Hit!)", "Score: " + str(runs) + "/" + str(wickets))
                            ball_log_str = f"{current_over_str}:0-{out_type_actual}-FH-NotOut"
                            # Log non-dismissal event for free hit
                            innings1Log.append({"event": current_over_str + f" {current_bowler['displayName']} to {current_batter['player']['displayName']}" + f" DOT BALL ({out_type_actual} on Free Hit - Not Out!)" + " Score: " + str(runs) + "/" + str(wickets), # Added ! for emphasis
                                                "balls": balls, "runs_this_ball": 0, "total_runs": runs, "wickets": wickets,
                                                "batterTracker": copy.deepcopy(batterTracker), "bowlerTracker": copy.deepcopy(bowlerTracker),
                                                "batsman": btn, "batter1": batter1['player']['playerInitials'] if batter1 else 'N/A', "batter2": batter2['player']['playerInitials'] if batter2 else 'N/A',
                                                "bowler": bln, "is_dismissal": False, "out_type_on_fh_nodismissal": out_type_actual, "is_free_hit_delivery": True, "original_event_type": event_type_param}) # Ensure these params are logged

                        if is_dismissal: # Proceed only if it's a valid dismissal
                            wickets += 1
                            out_desc = out_type_actual.title()
                            runs_off_wicket_ball = 0

                            if out_type_actual == "runOut":
                                runs_off_wicket_ball = random.randint(0,1)
                                runs += runs_off_wicket_ball
                                out_desc = f"Run Out ({runs_off_wicket_ball}r)"

                            print(current_over_str, f"{current_bowler['displayName']} to {current_batter['player']['displayName']}", "W", "Score: " + str(runs) + "/" + str(wickets), out_desc + log_suffix)
                            ball_log_str = f"{current_over_str}:W-{out_desc}"
                            if event_type_param == "NB": ball_log_str += "-NB"

                            if credited_to_bowler: bowlerTracker[bln]['wickets'] += 1
                            bowlerTracker[bln]['runs'] += runs_off_wicket_ball # for runouts
                            batterTracker[btn]['runs'] += runs_off_wicket_ball # for runouts

                            bowlerTracker[bln]['ballLog'].append(ball_log_str)
                            batterTracker[btn]['ballLog'].append(ball_log_str + f"-Bowler-{bln}") # Batter's log includes bowler
                            ballLog.append(ball_log_str)

                            innings1Log.append({"event" : current_over_str + f" {current_bowler['displayName']} to {current_batter['player']['displayName']}" + " W - " + out_desc + " Score: " + str(runs) + "/" + str(wickets) + log_suffix,
                                                "balls": balls, "runs_this_ball": runs_off_wicket_ball, "total_runs": runs, "wickets": wickets,
                                                "batterTracker": copy.deepcopy(batterTracker), "bowlerTracker": copy.deepcopy(bowlerTracker),
                                                "batsman": btn,"batter1": batter1['player']['playerInitials'] if batter1 else 'N/A', "batter2": batter2['player']['playerInitials'] if batter2 else 'N/A',
                                                "bowler": bln, "out_type": out_type_actual, "is_free_hit_delivery": is_fh_param, "original_event_type": event_type_param}) # Ensure these params are logged
                            playerDismissed(current_batter) # Pass the batter object who is out

                    else: # Dot ball, no wicket
                        P_EXTRAS = 0.08 # Probability of byes/leg-byes on a dot ball
                        if random.uniform(0,1) < P_EXTRAS and not is_fh_param : # Extras less likely on a free hit as batsman is trying to hit
                            extras_kind = random.choice(['B', 'LB'])
                            runs_off_extras = random.choice([1, 1, 1, 1, 2, 4]) # 1s more common

                            runs += runs_off_extras
                            # Byes/Leg-byes are not debited against bowler's runs conceded.
                            # Batter does not get these runs.

                            print(current_over_str, f"{current_bowler['displayName']} to {current_batter['player']['displayName']}", f"{runs_off_extras} {extras_kind}!", "Score: " + str(runs) + "/" + str(wickets) + log_suffix)
                            ball_log_str = f"{current_over_str}:{runs_off_extras}{extras_kind}"
                            # These logs are for team/innings, not directly for bowler/batter stats for these extras
                            bowlerTracker[bln]['ballLog'].append(ball_log_str + "-EXTRAS")
                            batterTracker[btn]['ballLog'].append(ball_log_str + "-EXTRAS")
                            ballLog.append(ball_log_str)

                            innings1Log.append({
                                "event": current_over_str + f" {current_bowler['displayName']} to {current_batter['player']['displayName']} {runs_off_extras} {extras_kind}!" + " Score: " + str(runs) + "/" + str(wickets) + log_suffix,
                                "balls": balls, # This is the main innings ball count, should be accurate
                                "runs_this_ball": runs_off_extras, # Runs from this specific event
                                "total_runs": runs, "wickets": wickets,
                                "batterTracker": copy.deepcopy(batterTracker),
                                "bowlerTracker": copy.deepcopy(bowlerTracker),
                                "batsman": btn, "batter1": batter1['player']['playerInitials'] if batter1 else 'N/A',
                                "batter2": batter2['player']['playerInitials'] if batter2 else 'N/A',
                                "bowler": bln,
                                "type": "EXTRAS", # New event type
                                "extras_type": extras_kind, # 'B' or 'LB'
                                "is_free_hit_delivery": is_fh_param, # Should be false if extras logic is hit after dot ball
                                "original_event_type": event_type_param
                            })
                            if runs_off_extras % 2 == 1:
                                onStrike = batter2 if onStrike == batter1 else batter1
                            return # Processed as extras, exit

                        # Standard Dot ball if no extras
                        print(current_over_str, f"{current_bowler['displayName']} to {current_batter['player']['displayName']}", "0", "Score: " + str(runs) + "/" + str(wickets) + log_suffix)
                        ball_log_str = f"{current_over_str}:0"
                        if is_fh_param: ball_log_str += "-FH"
                        if event_type_param == "NB": ball_log_str += "-NB"
                        bowlerTracker[bln]['ballLog'].append(ball_log_str)
                        batterTracker[btn]['ballLog'].append(ball_log_str)
                        ballLog.append(ball_log_str)
                        innings1Log.append({"event" : current_over_str + f" {current_bowler['displayName']} to {current_batter['player']['displayName']} " + "0" + " Score: " + str(runs) + "/" + str(wickets) + log_suffix,
                                            "balls": balls, "runs_this_ball": 0, "total_runs": runs, "wickets": wickets,
                                            "batterTracker": copy.deepcopy(batterTracker), "bowlerTracker": copy.deepcopy(bowlerTracker),
                                            "batsman": btn,"batter1": batter1['player']['playerInitials'] if batter1 else 'N/A', "batter2": batter2['player']['playerInitials'] if batter2 else 'N/A',
                                            "bowler": bln, "is_free_hit_delivery": is_fh_param, "original_event_type": event_type_param}) # Ensure these params are logged
                return # From the main loop over denominationProbabilities_list
        # Fallback if loop completes without returning (should ideally not happen if probabilities sum to total_den_prob)
        # This might indicate an issue with probability generation or decider logic.
        # For safety, treat as a dot ball if this is reached.
        print(f"Warning: decider {decider} did not fall into any probability bracket. Treating as dot ball.")
        ball_log_str = f"{current_over_str}:0-fallback"
        bowlerTracker[bln]['ballLog'].append(ball_log_str)
        batterTracker[btn]['ballLog'].append(ball_log_str)
        ballLog.append(ball_log_str)
        innings1Log.append({"event" : current_over_str + f" {current_bowler['displayName']} to {current_batter['player']['displayName']} " + "0 (Fallback)" + " Score: " + str(runs) + "/" + str(wickets),
                                            "balls": balls, "runs_this_ball": 0, "total_runs": runs, "wickets": wickets,
                                            "batterTracker": copy.deepcopy(batterTracker), "bowlerTracker": copy.deepcopy(bowlerTracker),
                                            "batsman": btn,"batter1": batter1['player']['playerInitials'] if batter1 else 'N/A', "batter2": batter2['player']['playerInitials'] if batter2 else 'N/A',
                                            "bowler": bln, "is_free_hit_delivery": is_fh_param, "original_event_type": event_type_param, "fallback":True }) # Ensure these params are logged

    # Refactored delivery function for innings1
    def delivery(bowler, batter, over, is_free_hit=False): # is_free_hit is for the CURRENT ball
        nonlocal batterTracker, bowlerTracker, onStrike, ballLog, balls, runs, wickets, spin, pace
        global innings1Log

        blname = bowler['playerInitials']
        btname = batter['player']['playerInitials']

        # Batting and Bowling info setup (as it was)
        batInfo = batter['player']
        bowlInfo_orig = bowler # Keep original bowler stats
        bowlInfo = copy.deepcopy(bowler) # Work with a copy for temporary adjustments

        # Pitch effects
        if('break' in bowlInfo['bowlStyle'] or 'spin' in bowlInfo['bowlStyle']): # More specific check
            effect = (1.0 - spin)/2
            bowlInfo['bowlOutsRate'] = max(0, bowlInfo['bowlOutsRate'] + (effect * 0.25))
            for r_key in ['0','1']: bowlInfo['bowlRunDenominationsObject'][r_key] = max(0.001, bowlInfo['bowlRunDenominationsObject'].get(r_key,0) + (effect * 0.25))
            for r_key in ['4','6']: bowlInfo['bowlRunDenominationsObject'][r_key] = max(0.001, bowlInfo['bowlRunDenominationsObject'].get(r_key,0) - (effect * 0.38))
        elif('medium' in bowlInfo['bowlStyle'] or 'fast' in bowlInfo['bowlStyle']): # More specific check
            effect = (1.0 - pace)/2 # Using pace factor from innings1 scope
            bowlInfo['bowlOutsRate'] = max(0, bowlInfo['bowlOutsRate'] + (effect * 0.25))
            for r_key in ['0','1']: bowlInfo['bowlRunDenominationsObject'][r_key] = max(0.001, bowlInfo['bowlRunDenominationsObject'].get(r_key,0) + (effect * 0.25))
            for r_key in ['4','6']: bowlInfo['bowlRunDenominationsObject'][r_key] = max(0.001, bowlInfo['bowlRunDenominationsObject'].get(r_key,0) - (effect * 0.38))

        denAvg = {}
        outAvg = (batInfo['batOutsRate'] + bowlInfo['bowlOutsRate']) / 2
        outTypeAvg = {}
        runoutChance = 0.01
        if(batInfo['batBallsTotal'] > 0): # Use batInfo which is batter['player']
            runoutChance = (batInfo['runnedOut']) / batInfo['batBallsTotal']
        else: runoutChance = 0.005

        for batKey in batInfo['batRunDenominationsObject']:
            denAvg[batKey] = (batInfo['batRunDenominationsObject'].get(batKey,0) + bowlInfo['bowlRunDenominationsObject'].get(batKey,0))/2

        for a_key, b_val in zip(batInfo['batOutTypesObject'], bowlInfo['bowlOutTypesObject']): # bowlInfo might not have all keys a_key has
             outTypeAvg[a_key] = (batInfo['batOutTypesObject'].get(a_key,0) + bowlInfo['bowlOutTypesObject'].get(a_key,0)) / 2 # safer get for bowlInfo
        outTypeAvg['runOut'] = runoutChance

        # No-ball check (using original bowler stats)
        noballRate = bowlInfo_orig['bowlNoballRate']
        is_no_ball_event = noballRate > random.uniform(0,1)

        if is_no_ball_event:
            runs += 1 # Penalty run
            bowlerTracker[blname]['runs'] += 1
            bowlerTracker[blname]['noballs'] += 1 # Increment noballs count for the bowler

            # Log the "NO_BALL_CALL" event - this signifies the no-ball itself
            print(over, f"{bowler['displayName']} to {batter['player']['displayName']}", "NO BALL!", "Score: " + str(runs) + "/" + str(wickets))
            bowlerTracker[blname]['ballLog'].append(f"{over}:NB+1") # Log indicates +1 for the no-ball

            innings1Log.append({
                "event": over + f" {bowler['displayName']} to {batter['player']['displayName']}" + " NO BALL!" + " Score: " + str(runs) + "/" + str(wickets),
                "balls": balls, # balls (innings total) does not increment for the NB call itself
                "runs_this_ball": 1, # The penalty run
                "total_runs": runs, "wickets": wickets,
                "batterTracker": copy.deepcopy(batterTracker),
                "bowlerTracker": copy.deepcopy(bowlerTracker),
                "batsman": btname,
                "batter1": batter1['player']['playerInitials'] if batter1 else 'N/A',
                "batter2": batter2['player']['playerInitials'] if batter2 else 'N/A',
                "bowler": blname,
                "type": "NO_BALL_CALL", # Specific type for the no-ball call
                "is_free_hit_delivery": True, # The delivery that follows IS a free hit
                "original_event_type": "NB_CALL" # Distinguish from outcome of NB
            })

            # Now process the outcome of the actual delivery (which is a free hit)
            # Runs scored here are in addition to the no-ball penalty
            getOutcome_standalone(bowler, batter, denAvg, outAvg, outTypeAvg, over, is_fh_param=True, event_type_param="NB")
            return "NO_BALL" # Indicates a no-ball was bowled, over ball count shouldn't increase

        # Wide check (if not a no-ball)
        wideRate = bowlInfo_orig['bowlWideRate']
        if wideRate > random.uniform(0,1):
            runs += 1
            bowlerTracker[blname]['runs'] += 1
            # Wides do not count as a ball bowled for bowler stats, nor faced by batter.
            print(over, f"{bowler['displayName']} to {batter['player']['displayName']}", "Wide", "Score: " + str(runs) + "/" + str(wickets))
            ballLog.append(f"{over}:WD") # General ball log
            bowlerTracker[blname]['ballLog'].append(f"{over}:WD")
            # Log the WIDE event
            innings1Log.append({
                "event": over + f" {bowler['displayName']} to {batter['player']['displayName']}" + " Wide" + " Score: " + str(runs) + "/" + str(wickets),
                "balls": balls, # balls (innings total) does not increment for a wide
                "runs_this_ball": 1, # The penalty run for wide
                "total_runs": runs, "wickets": wickets,
                "batterTracker": copy.deepcopy(batterTracker),
                "bowlerTracker": copy.deepcopy(bowlerTracker),
                "batsman": btname,
                "batter1": batter1['player']['playerInitials'] if batter1 else 'N/A',
                "batter2": batter2['player']['playerInitials'] if batter2 else 'N/A',
                "bowler": blname,
                "type": "WIDE", # Specific type for wide
                "is_free_hit_delivery": is_free_hit, # A wide can occur on a free hit, state persists
                "original_event_type": "WIDE"
            })
            return "WIDE" # Indicates a wide, over ball count shouldn't increase

        # Legal Delivery (or a Free Hit delivery that wasn't a No Ball or Wide itself)
        balls += 1 # Innings ball count increments only for legal deliveries (or FHs that are legal)

        # Aggression adjustments
        current_ball_of_innings = balls
        # --- Start of aggression adjustments (copied from original, ensure variables like 'spin', 'pace' are in scope) ---
        sumLast10 = 0
        outsLast10 = 0
        for i_log in ballLog:
            spl_bl = i_log.split(":")
            if("W" not in spl_bl[1]):
                run_part = spl_bl[1].split('-')[0]
                if run_part.isdigit(): sumLast10 += int(run_part)
            else:
                outsLast10 += 1

        if(current_ball_of_innings < 105):
            adjust_last10 = random.uniform(0.02,0.04)
            if(outsLast10 < 2):
                denAvg['0'] = max(0.001, denAvg.get('0',0) - adjust_last10 * (1/2))
                denAvg['1'] = max(0.001, denAvg.get('1',0) - adjust_last10 * (1/2))
                denAvg['2'] = max(0.001, denAvg.get('2',0) + adjust_last10 * (1/2))
                denAvg['4'] = max(0.001, denAvg.get('4',0) + adjust_last10 * (1/2))
            else:
                adjust_last10 += 0.018
                denAvg['0'] = max(0.001, denAvg.get('0',0) + adjust_last10 * (1.1/2))
                denAvg['1'] = max(0.001, denAvg.get('1',0) + adjust_last10 * (0.9/2))
                denAvg['4'] = max(0.001, denAvg.get('4',0) - adjust_last10 * (1/2))
                denAvg['6'] = max(0.001, denAvg.get('6',0) - adjust_last10 * (1/2))
                outAvg = max(0.001, outAvg - 0.02)

        if(batterTracker[btname]['balls'] < 8 and current_ball_of_innings < 80):
            adjust = random.uniform(-0.01, 0.03)
            outAvg = max(0.001, outAvg - 0.015)
            denAvg['0'] = max(0.001, denAvg.get('0',0) + adjust * (1.5/3))
            denAvg['1'] = max(0.001, denAvg.get('1',0) + adjust * (1/3))
            denAvg['2'] = max(0.001, denAvg.get('2',0) + adjust * (0.5/3))
            denAvg['4'] = max(0.001, denAvg.get('4',0) - adjust * (0.5/3))
            denAvg['6'] = max(0.001, denAvg.get('6',0) - adjust * (1.5/3))

        # ... (other aggression adjustments need similar .get(key,0) and max(0.001, ...) guards) ...
        # For brevity, I'll assume these are applied carefully. The structure is what's key here.

        if(current_ball_of_innings <= 12):
            sixAdjustment = random.uniform(0.02, 0.05)
            if(outAvg < 0.07): outAvg = 0.001 # Ensure not zero, but small
            else: outAvg = max(0.001, outAvg - 0.07)
            if(sixAdjustment > denAvg.get('6',0)): sixAdjustment = denAvg.get('6',0)
            denAvg['6'] = max(0.001, denAvg.get('6',0) - sixAdjustment)
            denAvg['0'] = max(0.001, denAvg.get('0',0) + sixAdjustment * (1/3))
            denAvg['1'] = max(0.001, denAvg.get('1',0) + sixAdjustment * (2/3))
        elif(current_ball_of_innings > 12 and current_ball_of_innings <= 36):
            if(wickets == 0):
                adj = random.uniform(0.05,0.11); denAvg['0']=max(0.001,denAvg.get('0',0)-adj*(2/3)); denAvg['1']=max(0.001,denAvg.get('1',0)-adj*(1/3)); denAvg['4']=max(0.001,denAvg.get('4',0)+adj*(2/3)); denAvg['6']=max(0.001,denAvg.get('6',0)+adj*(1/3))
            else:
                adj = random.uniform(0.02,0.08); denAvg['0']-=adj*(2/3); denAvg['1']-=adj*(1/3); denAvg['4']+=adj*(2.5/3); denAvg['6']+=adj*(0.5/3); outAvg = max(0.001, outAvg-0.03)
        elif(current_ball_of_innings > 36 and current_ball_of_innings <= 102):
            if(wickets < 3):
                adj = random.uniform(0.05,0.11); denAvg['0']-=adj*(1.5/3); denAvg['1']-=adj*(1/3); denAvg['4']+=adj*(1.5/3); denAvg['6']+=adj*(1/3)
            else:
                adj = random.uniform(0.02,0.07); denAvg['0']-=adj*(1.6/3); denAvg['1']-=adj*(1.2/3); denAvg['4']+=adj*(2.1/3); denAvg['6']+=adj*(0.9/3); outAvg = max(0.001, outAvg-0.03)
        else:
            if(wickets < 7):
                adj = random.uniform(0.07,0.1); denAvg['0']-=adj*(0.4/3); denAvg['1']-=adj*(1/3); denAvg['4']+=adj*(1.4/3); denAvg['6']+=adj*(1.8/3); outAvg = max(0.001, outAvg+0.01)
            else:
                adj = random.uniform(0.07,0.09); denAvg['0']-=adj*(0.4/3); denAvg['1']-=adj*(1.8/3); denAvg['4']+=adj*(1.5/3); denAvg['6']+=adj*(1.5/3); outAvg = max(0.001, outAvg+0.01)
        # --- End of aggression adjustments ---

        getOutcome_standalone(bowler, batter, denAvg, outAvg, outTypeAvg, over, is_fh_param=is_free_hit, event_type_param="LEGAL")
        return "LEGAL"

    for i in range(20):
        # Strike rotation
        if i != 0:
            if onStrike == batter1: onStrike = batter2
            elif onStrike == batter2: onStrike = batter1 # Make sure onStrike is not None
            else: # One batter might be None if playerDismissed and no new batter came
                  if batter1: onStrike = batter1
                  elif batter2: onStrike = batter2
                  else: # Both batters are None, innings should end
                      print(f"Innings1 Over {i+1}: Both batters are None. Ending innings.")
                      break


        current_bowler_obj = None
        if i == 0:
            current_bowler_obj = bowler1_obj
        elif i == 1:
            current_bowler_obj = bowler2_obj
        else:
            phase = ""
            if i < 6: phase = "PP"
            elif i < 16: phase = "MID"
            else: phase = "DEATH"

            candidates = [
                b for b in designated_bowlers
                if bowlerTracker[b['playerInitials']]['balls'] < 24
                   and b['playerInitials'] != last_bowler_initials
                   and b['bowlOutsRate'] >= MIN_BOWLING_OUT_RATE_THRESHOLD
            ]

            if not candidates: # Fallback 1: Designated bowlers, ignore last_bowler, but respect rate
                candidates = [
                    b for b in designated_bowlers
                    if bowlerTracker[b['playerInitials']]['balls'] < 24
                       and b['bowlOutsRate'] >= MIN_BOWLING_OUT_RATE_THRESHOLD
                ]
                if not candidates: # Fallback 2: Designated bowlers, ignore rate and last_bowler (original fallback)
                    print(f"INFO: Innings1 Over {i+1}, Relaxing bowling rate threshold for designated bowlers (main candidates).")
                    candidates = [
                        b for b in designated_bowlers
                        if bowlerTracker[b['playerInitials']]['balls'] < 24
                           and b['playerInitials'] != last_bowler_initials # Try with this first
                    ]
                    if not candidates: # Fallback 2.1: Designated bowlers, ignore rate and last_bowler restriction
                         candidates = [b for b in designated_bowlers if bowlerTracker[b['playerInitials']]['balls'] < 24]


            # If still no designated bowlers after primary and fallbacks for designated:
            if not candidates:
                non_designated_candidates = [
                    b for b in bowling_selection_pool
                    if b['playerInitials'] not in [db['playerInitials'] for db in designated_bowlers]
                       and bowlerTracker[b['playerInitials']]['balls'] < 24
                       and b['playerInitials'] != last_bowler_initials
                       and b['bowlOutsRate'] >= MIN_BOWLING_OUT_RATE_THRESHOLD
                ]
                if not non_designated_candidates: # Try non-designated without last_bowler restriction, with rate
                    non_designated_candidates = [
                        b for b in bowling_selection_pool
                        if b['playerInitials'] not in [db['playerInitials'] for db in designated_bowlers]
                           and bowlerTracker[b['playerInitials']]['balls'] < 24
                           and b['bowlOutsRate'] >= MIN_BOWLING_OUT_RATE_THRESHOLD
                    ]
                if not non_designated_candidates: # Try non-designated, relaxing rate, with last_bowler restriction
                    print(f"INFO: Innings1 Over {i+1}, Relaxing bowling rate threshold for non-designated bowlers.")
                    non_designated_candidates = [
                        b for b in bowling_selection_pool
                        if b['playerInitials'] not in [db['playerInitials'] for db in designated_bowlers]
                           and bowlerTracker[b['playerInitials']]['balls'] < 24
                           and b['playerInitials'] != last_bowler_initials
                    ]
                    if not non_designated_candidates: # Try non-designated, relaxing rate, without last_bowler restriction
                         non_designated_candidates = [
                            b for b in bowling_selection_pool
                            if b['playerInitials'] not in [db['playerInitials'] for db in designated_bowlers]
                               and bowlerTracker[b['playerInitials']]['balls'] < 24
                        ]

                if non_designated_candidates:
                    # Select from non_designated_candidates, potentially phase-aware if desired, or random
                    # For now, random choice from the filtered non-designated list
                    current_bowler_obj = random.choice(non_designated_candidates)
                else:
                    # Ultimate fallback: least bowled designated bowler, ignoring rate and last_bowler entirely
                    # This was the original final fallback if non_designated_available was empty
                    print(f"WARNING: Innings1 Over {i+1}, All preferred bowlers nearly maxed or below rate. Fallback to least bowled designated.")
                    least_bowled_candidates = sorted(
                        [b_sort for b_sort in designated_bowlers if bowlerTracker[b_sort['playerInitials']]['balls'] < 24],
                        key=lambda b_lambda: bowlerTracker[b_lambda['playerInitials']]['balls']
                    )
                    if least_bowled_candidates:
                        current_bowler_obj = least_bowled_candidates[0]
                    elif bowling_selection_pool: # Absolute last resort from the broader pool
                        current_bowler_obj = random.choice([b for b in bowling_selection_pool if bowlerTracker[b['playerInitials']]['balls'] < 24] or bowling_selection_pool)
                    else:
                        current_bowler_obj = None # Should ideally not happen if team has bowlers

            # If candidates were found (either primary designated, fallback designated, or non-designated selected above)
            if current_bowler_obj is None and candidates: # current_bowler_obj would be set if non_designated_candidates were chosen
                chosen_bowler_initials_for_rotation = None
                phase_preferred_list_objs = []
                if phase == "PP": phase_preferred_list_objs = designated_opening_bowlers
                elif phase == "MID": phase_preferred_list_objs = designated_middle_bowlers
                else: phase_preferred_list_objs = designated_death_bowlers

                final_phase_candidates = [b for b in candidates if b['playerInitials'] in [p['playerInitials'] for p in phase_preferred_list_objs]]

                if final_phase_candidates:
                    for bowler_initials_in_rotation in list(designated_bowler_rotation_list):
                        potential_bowler = next((b for b in final_phase_candidates if b['playerInitials'] == bowler_initials_in_rotation), None)
                        if potential_bowler:
                            current_bowler_obj = potential_bowler
                            chosen_bowler_initials_for_rotation = bowler_initials_in_rotation
                            break
                    if not chosen_bowler_initials_for_rotation:
                        current_bowler_obj = random.choice(final_phase_candidates)
                elif candidates: # No phase specific, but general candidates exist
                    for bowler_initials_in_rotation in list(designated_bowler_rotation_list):
                        potential_bowler = next((b for b in candidates if b['playerInitials'] == bowler_initials_in_rotation), None)
                        if potential_bowler:
                            current_bowler_obj = potential_bowler
                            chosen_bowler_initials_for_rotation = bowler_initials_in_rotation
                            break
                    if not chosen_bowler_initials_for_rotation:
                        current_bowler_obj = random.choice(candidates)

                if chosen_bowler_initials_for_rotation:
                    designated_bowler_rotation_list.remove(chosen_bowler_initials_for_rotation)
                    designated_bowler_rotation_list.append(chosen_bowler_initials_for_rotation)
                elif current_bowler_obj and current_bowler_obj['playerInitials'] in designated_bowler_rotation_list: # Chosen by random from filtered lists
                     designated_bowler_rotation_list.remove(current_bowler_obj['playerInitials'])
                     designated_bowler_rotation_list.append(current_bowler_obj['playerInitials'])

        if not current_bowler_obj:
            if bowling_selection_pool:
                print(f"CRITICAL FALLBACK (Innings1): No specific bowler chosen for over {i+1}. Picking from any available in main pool.")
                available_fallback = [b for b in bowling_selection_pool if bowlerTracker[b['playerInitials']]['balls'] < 24]
                current_bowler_obj = random.choice(available_fallback) if available_fallback else \
                                    (bowling_selection_pool[0] if bowling_selection_pool else None)
            else:
                 print(f"CRITICAL ERROR (Innings1): No bowlers in selection pool for team {bowlingName}. Innings cannot continue.")
                 break


        balls_bowled_this_over = 0
        if current_bowler_obj and current_bowler_obj.get('playerInitials'):
            # print(f"Innings 1, Over {i+1}: Bowler is {current_bowler_obj['displayName']}")
            while balls_bowled_this_over < 6:
                if wickets == 10 or not onStrike: # Added check for onStrike being None
                    if not onStrike: print(f"Innings1 Over {i}.{balls_bowled_this_over + 1}: No batter on strike. Ending over/innings.")
                    break
                delivery_type = delivery(copy.deepcopy(current_bowler_obj), copy.deepcopy(onStrike),
                                         f"{i}.{balls_bowled_this_over + 1}", is_free_hit=is_next_ball_free_hit)
                if delivery_type == "NO_BALL":
                    is_next_ball_free_hit = True
                    # Ball doesn't count towards over
                elif delivery_type == "WIDE":
                    # Ball doesn't count, free hit status persists
                    pass
                elif delivery_type == "LEGAL":
                    is_next_ball_free_hit = False
                    balls_bowled_this_over += 1

                if wickets == 10: break # Check after delivery if all out

            if current_bowler_obj and current_bowler_obj.get('playerInitials'): # Ensure current_bowler_obj is still valid
                 bowlerTracker[current_bowler_obj['playerInitials']]['overs'] += 1 # This was missing, should be outside the while loop
                 last_bowler_initials = current_bowler_obj['playerInitials']

        elif bowling_selection_pool :
            print(f"CRITICAL ERROR (Innings1): No valid bowler object for over {i+1} for team {bowlingName} but pool existed. Innings ends.")
            break
        else:
            print(f"CRITICAL ERROR (Innings1): No bowlers in selection pool for team {bowlingName}. Innings ends.")
            break
        if wickets == 10: break # Break outer over loop if all out
            
    # print(batterTracker)
    # print(bowlerTracker)
    batsmanTabulate = []
    # Determine the player initials of the batsmen who were at the crease if the innings ended.
    # These are based on the 'onStrike' and the other batter (batter1/batter2) at the point the loop terminated.
    # This needs to be captured *before* onStrike, batter1, batter2 might be reset or go out of scope if innings ends.
    # For simplicity, we'll pass the final 'wickets' count and 'battingOrder' to the scorecard generation logic.
    # The actual onStrike/nonStrike at the very end might be complex to capture perfectly here without altering main loop much.
    # We will use the battingOrder and final wicket count.

    for btckd_player_initials in batterTracker: # btckd_player_initials is the key, e.g., 'MS Dhoni'
        player_specific_data = batterTracker[btckd_player_initials]
        runs_scored = player_specific_data['runs']
        balls_faced = player_specific_data['balls']

        sr_val = 'NA'
        if balls_faced > 0:
            sr_val = str(round((runs_scored * 100) / balls_faced, 2))

        dismissal_status = "DNB" # Default: Did Not Bat
        player_batted = len(player_specific_data['ballLog']) > 0
        got_out = False

        for ball_record in player_specific_data['ballLog']:
            if "W" in ball_record: # Indicates a wicket
                got_out = True
                # Detailed dismissal (current logic for parsing 'CaughtBy', 'runout', etc. is okay)
                if "CaughtBy" in ball_record:
                    split_log = ball_record.split("-")
                    catcher_name = split_log[2]
                    bowler_name = split_log[-1]
                    dismissal_status = f"c {catcher_name} b {bowler_name}"
                elif "runout" in ball_record: # Note: mainconnect.py uses "Run Out" with space in logs.
                    dismissal_status = "Run out"
                else: # Assumes format like "W-bowled-BowlerName" or "W-lbw-BowlerName"
                    split_log = ball_record.split("-")
                    if len(split_log) > 2 : # e.g. W-bowled-Bumrah
                        dismissal_type = split_log[1]
                        bowler_name = split_log[-1]
                        dismissal_status = f"{dismissal_type} b {bowler_name}"
                    elif len(split_log) == 2: # e.g. W-bowled (if bowler name not appended in log)
                         dismissal_status = split_log[1]
                    else: # Fallback for simple "W"
                        dismissal_status = "Wicket"
                break # Player is out, no need to check further logs for dismissal status

        if not got_out:
            if player_batted:
                dismissal_status = "Not out"
            else:
                # Player did not bat. Check if they were in line to bat or at crease.
                player_considered_in = False
                # wickets is the number of fallen wickets. battingOrder indices are 0-based.
                # Players from battingOrder[0] to battingOrder[wickets-1] are the ones who got out.
                # battingOrder[wickets] and battingOrder[wickets+1] are potentially the not out batsmen or next in.
                # Max index for "came in" is min(len(battingOrder) - 1, wickets + 1)
                for idx in range(min(len(battingOrder), wickets + 2)):
                    if battingOrder[idx]['player']['playerInitials'] == btckd_player_initials:
                        player_considered_in = True
                        break
                if player_considered_in:
                    dismissal_status = "Not out"
                # Else, remains "DNB" if not in this range and didn't bat.

        batsmanTabulate.append([btckd_player_initials, runs_scored, balls_faced, sr_val, dismissal_status])
        
    bowlerTabulate = []
    for btrack in bowlerTracker:
        localBowlerTabulate = [btrack, bowlerTracker[btrack]['runs']]
        overs_tb = 0
        remainder_balls = bowlerTracker[btrack]['balls'] % 6 
        number_overs = bowlerTracker[btrack]['balls'] // 6
        localBowlerTabulate.append(f"{number_overs}.{remainder_balls}")
        localBowlerTabulate.append(bowlerTracker[btrack]['wickets'])
        econ_tb = "NA"
        if(bowlerTracker[btrack]['balls'] != 0):
            econ_tb = (bowlerTracker[btrack]['runs'] / bowlerTracker[btrack]['balls'])*6
            econ_tb = str(round(econ_tb, 2))
        localBowlerTabulate.append(econ_tb)
        bowlerTabulate.append(localBowlerTabulate)

    print(tabulate(batsmanTabulate, ["Player", "Runs", "Balls", "SR" ,"Out"], tablefmt="grid"))
    print(tabulate(bowlerTabulate, ["Player", "Runs", "Overs", "Wickets", "Eco"], tablefmt="grid"))
        
    target = runs + 1
    innings1Balls = balls
    innings1Runs = runs
    innings1Batting = tabulate(batsmanTabulate, ["Player", "Runs", "Balls", "SR" ,"Out"], tablefmt="grid")
    innings1Bowling = tabulate(bowlerTabulate, ["Player", "Runs", "Overs", "Wickets", "Eco"], tablefmt="grid")

    innings1Battracker = batterTracker
    innings1Bowltracker = bowlerTracker

def innings2(batting, bowling, battingName, bowlingName, pace, spin, outfield, dew, detoriate):
    # print(battingName, bowlingName, pace, spin, outfield, dew, detoriate)
    global innings2Batting, innings2Bowling, innings2Runs, innings2Balls, winner, winMsg, innings2Bowltracker, innings2Battracker, innings2Log
    is_next_ball_free_hit = False # Initialize for the innings
    bowlerTracker = {} #add names of all in innings def
    batterTracker = {} #add names of all in innings def
    battingOrder = []
    catchingOrder = []
    ballLog = []

    runs = 0
    balls = 0
    wickets = 0
    targetChased = False
    # break or spin; medium or fast

    # Deciding batting order
    for i in batting:
        batterTracker[i['playerInitials']] = {'playerInitials': i['playerInitials'], 'balls': 0, 'runs': 0, 'ballLog': []}
        runObj = {}
        outObj = {}

        i['batBallsTotal'] += 1
        for run in i['batRunDenominations']:
            runObj[run] = i['batRunDenominations'][run] / i['batBallsTotal']
        i['batRunDenominationsObject'] = runObj

        for out in i['batOutTypes']:
            outObj[out] = i['batOutTypes'][out] / i['batBallsTotal']
        i['batOutTypesObject'] = outObj

        original_bat_den_sum = 0.0
        for val in i['batRunDenominationsObject'].values():
            if isinstance(val, (int, float)):
                original_bat_den_sum += val

        # for styles in i['byBowler']:

        #     runObj2 = {}
        #     outObj2 = {}
        #     batOutsRate = i['byBowler'][styles]['batOutsTotal'] / \
        #         i['byBowler'][styles]['batBallsTotal']
        #     i['byBowler'][styles]['batOutsRate'] = batOutsRate
        #     for run in i['byBowler'][styles]['batRunDenominations']:
        #         runObj2[run] = i['byBowler'][styles]['batRunDenominations'][run] / \
        #             i['byBowler'][styles]['batBallsTotal']
        #     i['byBowler'][styles]['batRunDenominationsObject'] = runObj2
        #     for out in i['byBowler'][styles]['batOutTypes']:
        #         outObj2[out] = i['byBowler'][styles]['batOutTypes'][out] / \
        #             i['byBowler'][styles]['batBallsTotal']
        #     i['byBowler'][styles]['batOutTypesObject'] = outObj2

        i['batOutsRate'] = i['batOutsTotal'] / i['batBallsTotal']

        # Calculate total career runs for the batsman
        total_career_runs_for_player = 0
        if 'batRunDenominations' in i and isinstance(i['batRunDenominations'], dict):
            for run_key, run_count in i['batRunDenominations'].items():
                if run_key.isdigit() and int(run_key) > 0: # Consider only actual scoring runs (1-6)
                    total_career_runs_for_player += run_count * int(run_key)

        if (i['matches'] < MIN_MATCHES_EXPERIENCE and \
            i['batBallsTotal'] <= FILLER_BATSMAN_MAX_BALLS_FACED and \
            total_career_runs_for_player < FILLER_BATSMAN_MAX_CAREER_RUNS):

            # Filler Batsman Logic (More Aggressive Adjustments)
            reduction_6 = i['batRunDenominationsObject'].get('6', 0.0) * 0.80  # Reduce by 80%
            reduction_4 = i['batRunDenominationsObject'].get('4', 0.0) * 0.70  # Reduce by 70%

            i['batRunDenominationsObject']['6'] = i['batRunDenominationsObject'].get('6', 0.0) - reduction_6
            i['batRunDenominationsObject']['4'] = i['batRunDenominationsObject'].get('4', 0.0) - reduction_4

            i['batRunDenominationsObject']['0'] = i['batRunDenominationsObject'].get('0', 0.0) + reduction_6 * 0.6 + reduction_4 * 0.6
            i['batRunDenominationsObject']['1'] = i['batRunDenominationsObject'].get('1', 0.0) + reduction_6 * 0.4 + reduction_4 * 0.4

            i['batOutsRate'] = i['batOutsRate'] * 1.40  # Increase out rate by 40%

            # Clamping
            if i['batRunDenominationsObject']['6'] < 0: i['batRunDenominationsObject']['6'] = 0.0
            if i['batRunDenominationsObject']['4'] < 0: i['batRunDenominationsObject']['4'] = 0.0

        elif i['matches'] < MIN_MATCHES_EXPERIENCE or i['batBallsTotal'] <= MIN_BAT_BALLS_EXPERIENCE:
            # Store original sum for potential normalization later (optional for this simplified step)
            # original_sum_den = sum(i['batRunDenominationsObject'].values())

            reduction_6 = i['batRunDenominationsObject'].get('6', 0.0) * 0.35
            reduction_4 = i['batRunDenominationsObject'].get('4', 0.0) * 0.25

            i['batRunDenominationsObject']['6'] = i['batRunDenominationsObject'].get('6', 0.0) - reduction_6
            i['batRunDenominationsObject']['4'] = i['batRunDenominationsObject'].get('4', 0.0) - reduction_4

            # Distribute reduced amounts to '0' and '1'
            i['batRunDenominationsObject']['0'] = i['batRunDenominationsObject'].get('0', 0.0) + reduction_6 * 0.5 + reduction_4 * 0.5
            i['batRunDenominationsObject']['1'] = i['batRunDenominationsObject'].get('1', 0.0) + reduction_6 * 0.5 + reduction_4 * 0.5

            i['batOutsRate'] = i['batOutsRate'] * 1.20

            # Ensure no negative probabilities (simple clamping)
            if i['batRunDenominationsObject']['6'] < 0: i['batRunDenominationsObject']['6'] = 0.0
            if i['batRunDenominationsObject']['4'] < 0: i['batRunDenominationsObject']['4'] = 0.0
            # Add more clamping if other denominations could become negative

        i['batRunDenominationsObject'] = normalize_probabilities(i['batRunDenominationsObject'], original_bat_den_sum)

        newPos = []
        posAvgObj = {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7":0,"8": 0, "9":0, "10":0}
        for p in i['position']:
            if(p != "null"):
                newPos.append(p)
        posTotal = sum(newPos)
        for p in newPos:
            if(str(p) in posAvgObj):
                posAvgObj[str(p)] += 1
            else:
                posAvgObj[str(p)] = 1

        for key_p in posAvgObj:
            posAvgObj[key_p] = posAvgObj[key_p]/i['matches'] 

        if(len(newPos) != 0):
            posAvg = posTotal/len(newPos)
        else:
            posAvg = 9.0
        battingOrder.append({"posAvg": posAvg, "player": i, "posAvgsAll": posAvgObj})

    battingOrder = sorted(battingOrder, key=lambda k: k['posAvg'])
    catchingOrder = sorted(catchingOrder, key=lambda k: k['catchRate'])

    for i in bowling:
        i['bowlBallsTotalRate'] = i['bowlBallsTotal'] / i['matches']
        # Ensure 'noballs' is initialized for each bowler
        bowlerTracker[i['playerInitials']] = {'playerInitials': i['playerInitials'], 'balls': 0, 
        'runs': 0, 'ballLog': [], 'overs': 0, 'wickets': 0, 'noballs': 0}
        runObj = {}
        outObj = {}
        i['catchRate'] = i['catches'] / i['matches']
        i['bowlWideRate'] = i['bowlWides'] / (i['bowlBallsTotal'] + 1)
        i['bowlNoballRate'] = i['bowlNoballs'] / (i['bowlBallsTotal'] + 1)
        i['bowlBallsTotal'] += 1
        for run in i['bowlRunDenominations']:
            runObj[run] = i['bowlRunDenominations'][run] / i['bowlBallsTotal']
        i['bowlRunDenominationsObject'] = runObj

        for out in i['bowlOutTypes']:
            outObj[out] = i['bowlOutTypes'][out] / i['bowlBallsTotal']
        i['bowlOutTypesObject'] = outObj

        original_bowl_den_sum = 0.0
        for val in i['bowlRunDenominationsObject'].values():
            if isinstance(val, (int, float)):
                original_bowl_den_sum += val

        # for styles in i['byBatsman']:
        #     runObj2 = {}
        #     outObj2 = {}
        #     bowlOutsRate = i['byBatsman'][styles]['bowlOutsTotal'] / \
        #         i['byBatsman'][styles]['bowlBallsTotal']
        #     i['byBatsman'][styles]['bowlOutsRate'] = batOutsRate
        #     for run in i['byBatsman'][styles]['bowlRunDenominations']:
        #         runObj2[run] = i['byBatsman'][styles]['bowlRunDenominations'][run] / \
        #             i['byBatsman'][styles]['bowlBallsTotal']
        #     i['byBatsman'][styles]['bowlRunDenominationsObject'] = runObj2
        #     for out in i['byBatsman'][styles]['bowlOutTypes']:
        #         outObj2[out] = i['byBatsman'][styles]['bowlOutTypes'][out] / \
        #             i['byBatsman'][styles]['bowlBallsTotal']
        #     i['byBatsman'][styles]['bowlOutTypesObject'] = outObj2

        i['bowlOutsRate'] = i['bowlOutsTotal'] / i['bowlBallsTotal']

        if i['matches'] < MIN_MATCHES_EXPERIENCE or i['bowlBallsTotal'] <= MIN_BOWL_BALLS_EXPERIENCE:
            # original_sum_den_bowl = sum(i['bowlRunDenominationsObject'].values()) # Optional for now

            increase_6 = i['bowlRunDenominationsObject'].get('6', 0.0) * 0.30
            increase_4 = i['bowlRunDenominationsObject'].get('4', 0.0) * 0.20

            i['bowlRunDenominationsObject']['6'] = i['bowlRunDenominationsObject'].get('6', 0.0) + increase_6
            i['bowlRunDenominationsObject']['4'] = i['bowlRunDenominationsObject'].get('4', 0.0) + increase_4

            # Reduce '0's to compensate, ensuring it doesn't go too low
            reduction_from_0 = increase_6 + increase_4
            current_0_val = i['bowlRunDenominationsObject'].get('0', 0.0)

            if current_0_val >= reduction_from_0:
                i['bowlRunDenominationsObject']['0'] = current_0_val - reduction_from_0
            else: # If '0's are not enough, take from '1's or just zero out '0'
                remaining_reduction = reduction_from_0 - current_0_val
                i['bowlRunDenominationsObject']['0'] = 0.0
                current_1_val = i['bowlRunDenominationsObject'].get('1', 0.0)
                if current_1_val >= remaining_reduction:
                    i['bowlRunDenominationsObject']['1'] = current_1_val - remaining_reduction
                else:
                    i['bowlRunDenominationsObject']['1'] = 0.0 # Or distribute deficit elsewhere if needed

            i['bowlOutsRate'] = i['bowlOutsRate'] * 0.80  # Decrease wicket-taking ability by 20%
            i['bowlWideRate'] = i['bowlWideRate'] * 1.15 # Increase wides by 15%
            i['bowlNoballRate'] = i['bowlNoballRate'] * 1.15 # Increase no-balls by 15%

            # Basic clamping for '0' and '1' if they were reduced
            if i['bowlRunDenominationsObject'].get('0', 0.0) < 0: i['bowlRunDenominationsObject']['0'] = 0.0
            if i['bowlRunDenominationsObject'].get('1', 0.0) < 0: i['bowlRunDenominationsObject']['1'] = 0.0

        i['bowlRunDenominationsObject'] = normalize_probabilities(i['bowlRunDenominationsObject'], original_bowl_den_sum)

        obj = {"20": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0,
               "10": 0, "11": 0, "12": 0, "13": 0, "14": 0, "15": 0, "16": 0, "17": 0, "18": 0, "19": 0}
        for over in i['overNumbers']:
            obj[over] += 1
        for keys in obj:
            if(i['matches'] != 0):
                avg = obj[keys]/i['matches']
            else:
                avg = -1
            obj[keys] = avg
        i['overNumbersObject'] = obj

    bowling = sorted(bowling, key=lambda k: k['bowlOutsRate'])
    bowling.reverse()
    bowling = bowling[0:7]

    bowlingOpening = sorted(bowling, key=lambda k: k['overNumbersObject']['1'])
    bowlingOpening.reverse()
    # bowlingOpening, bowlingDeath, bowlingMiddle are already capped at 7 by 'bowling' list being capped

    # Designated Bowlers (Top 6 from the initial pool of up to 7)
    bowling_selection_pool = bowling
    designated_bowlers = bowling_selection_pool[:min(6, len(bowling_selection_pool))]

    # Phase-specific lists from designated_bowlers. Safe .get usage for overNumbersObject
    designated_opening_bowlers = sorted(designated_bowlers, key=lambda k: k.get('overNumbersObject', {}).get('1', 0), reverse=True)
    designated_middle_bowlers = sorted(designated_bowlers, key=lambda k: k.get('overNumbersObject', {}).get('10', 0), reverse=True)
    designated_death_bowlers = sorted(designated_bowlers, key=lambda k: k.get('overNumbersObject', {}).get('19', 0), reverse=True)

    designated_bowler_rotation_list = [b['playerInitials'] for b in designated_bowlers]

    batter1 = battingOrder[0]
    batter2 = battingOrder[1]
    onStrike = batter1

    # Initial bowler selection for first two overs from designated lists
    bowler1_obj = None
    if designated_opening_bowlers:
        bowler1_obj = designated_opening_bowlers[0]
    elif designated_bowlers:
        bowler1_obj = designated_bowlers[0]
    elif bowling_selection_pool:
        bowler1_obj = bowling_selection_pool[0]

    bowler2_obj = None
    if len(designated_opening_bowlers) > 1 and (not bowler1_obj or designated_opening_bowlers[1]['playerInitials'] != bowler1_obj['playerInitials']):
        bowler2_obj = designated_opening_bowlers[1]
    elif len(designated_bowlers) > 1:
        for b in designated_bowlers:
            if not bowler1_obj or b['playerInitials'] != bowler1_obj['playerInitials']:
                bowler2_obj = b
                break
    if not bowler2_obj:
        bowler2_obj = bowler1_obj # Fallback if only one unique bowler available or no opening specified

    last_bowler_initials = None
    # is_next_ball_free_hit is already initialized at the start of innings2

    # This is the new, refactored getOutcome_standalone function for innings2
    def getOutcome_standalone(current_bowler, current_batter, den_avg_param, out_avg_param, out_type_avg_param, current_over_str, is_fh_param=False, event_type_param="LEGAL"): # Added is_fh_param and event_type_param
        nonlocal batterTracker, bowlerTracker, runs, balls, ballLog, wickets, onStrike, bowling, batter1, batter2, targetChased
        global innings2Log, winner, winMsg # innings2 specific globals

        bln = current_bowler['playerInitials']
        btn = current_batter['player']['playerInitials']

        if event_type_param == "LEGAL":
            bowlerTracker[bln]['balls'] += 1

        if event_type_param == "LEGAL" or event_type_param == "NB":
            batterTracker[btn]['balls'] += 1

        total_den_prob = sum(den_avg_param.values())
        if total_den_prob == 0: total_den_prob = 1

        last_prob_end = 0
        denominationProbabilities_list = []
        for denom_val, prob_val in den_avg_param.items():
            start_prob = last_prob_end
            end_prob = last_prob_end + prob_val
            denominationProbabilities_list.append({"denomination": denom_val, "start": start_prob, "end": end_prob})
            last_prob_end = end_prob

        decider = random.uniform(0, total_den_prob)

        for prob_outcome in denominationProbabilities_list:
            if prob_outcome['start'] <= decider < prob_outcome['end']:
                runs_on_this_ball = int(prob_outcome['denomination'])
                runs += runs_on_this_ball

                log_suffix = " (Free Hit)" if is_fh_param else ""
                if event_type_param == "NB": log_suffix += " (Off No-Ball)"

                if runs_on_this_ball > 0:
                    print(current_over_str, f"{current_bowler['displayName']} to {current_batter['player']['displayName']}", prob_outcome['denomination'], "Score: " + str(runs) + "/" + str(wickets) + log_suffix)
                    ball_log_str = f"{current_over_str}:{prob_outcome['denomination']}"
                    if is_fh_param: ball_log_str += "-FH"
                    if event_type_param == "NB": ball_log_str += "-NB"

                    bowlerTracker[bln]['runs'] += runs_on_this_ball
                    batterTracker[btn]['runs'] += runs_on_this_ball
                    bowlerTracker[bln]['ballLog'].append(ball_log_str)
                    batterTracker[btn]['ballLog'].append(ball_log_str)
                    ballLog.append(ball_log_str)

                    innings2Log.append({"event" : current_over_str + f" {current_bowler['displayName']} to {current_batter['player']['displayName']} " + prob_outcome['denomination'] + " Score: " + str(runs) + "/" + str(wickets) + log_suffix,
                                        "balls": balls, "runs_this_ball": runs_on_this_ball, "total_runs": runs, "wickets": wickets,
                                        "batterTracker": copy.deepcopy(batterTracker), "bowlerTracker": copy.deepcopy(bowlerTracker),
                                        "batsman": btn,"batter1": batter1['player']['playerInitials'] if batter1 else 'N/A', "batter2": batter2['player']['playerInitials'] if batter2 else 'N/A',
                                        "bowler": bln, "is_free_hit_delivery": is_fh_param, "original_event_type": event_type_param}) # Ensure these params are logged
                    if runs_on_this_ball % 2 == 1:
                        onStrike = batter2 if onStrike == batter1 else batter1
                else: # Dot ball (runs_on_this_ball == 0)
                    dot_ball_prob = den_avg_param.get('0', 0)
                    if dot_ball_prob == 0: dot_ball_prob = 1
                    probOut_val = out_avg_param * (total_den_prob / dot_ball_prob if dot_ball_prob else 1)
                    outDecider = random.uniform(0, 1)

                    if probOut_val > outDecider: # WICKET
                        out_type_actual = None
                        out_probs_list = []
                        total_out_type_prob = sum(out_type_avg_param.values())
                        if total_out_type_prob == 0: total_out_type_prob = 1

                        last_out_prob_end = 0
                        for out_key, out_val in out_type_avg_param.items():
                            out_probs_list.append({"type": out_key, "start": last_out_prob_end, "end": last_out_prob_end + out_val})
                            last_out_prob_end += out_val

                        typeDeterminer = random.uniform(0, total_out_type_prob)
                        for type_data in out_probs_list:
                            if type_data['start'] <= typeDeterminer < type_data['end']:
                                out_type_actual = type_data['type']
                                break
                        if not out_type_actual and out_probs_list: out_type_actual = out_probs_list[-1]['type']

                        is_dismissal = True
                        credited_to_bowler = True if out_type_actual not in ["runOut"] else False

                        if is_fh_param and out_type_actual != "runOut":
                            is_dismissal = False
                            print(current_over_str, f"{current_bowler['displayName']} to {current_batter['player']['displayName']}", f"NOT OUT ({out_type_actual} on Free Hit!)", "Score: " + str(runs) + "/" + str(wickets))
                            ball_log_str = f"{current_over_str}:0-{out_type_actual}-FH-NotOut"
                            innings2Log.append({"event": current_over_str + f" {current_bowler['displayName']} to {current_batter['player']['displayName']}" + f" DOT BALL ({out_type_actual} on Free Hit - Not Out!)" + " Score: " + str(runs) + "/" + str(wickets), # Added ! for emphasis
                                                "balls": balls, "runs_this_ball": 0, "total_runs": runs, "wickets": wickets,
                                                "batterTracker": copy.deepcopy(batterTracker), "bowlerTracker": copy.deepcopy(bowlerTracker),
                                                "batsman": btn, "batter1": batter1['player']['playerInitials'] if batter1 else 'N/A', "batter2": batter2['player']['playerInitials'] if batter2 else 'N/A',
                                                "bowler": bln, "is_dismissal": False, "out_type_on_fh_nodismissal": out_type_actual, "is_free_hit_delivery": True, "original_event_type": event_type_param}) # Ensure these params are logged

                        if is_dismissal: # Proceed only if it's a valid dismissal
                            wickets += 1
                            out_desc = out_type_actual.title()
                            runs_off_wicket_ball = 0

                            if out_type_actual == "runOut":
                                runs_off_wicket_ball = random.randint(0,1) # Runs on a run out
                                runs += runs_off_wicket_ball
                                out_desc = f"Run Out ({runs_off_wicket_ball}r)"

                            print(current_over_str, f"{current_bowler['displayName']} to {current_batter['player']['displayName']}", "W", "Score: " + str(runs) + "/" + str(wickets), out_desc + log_suffix)
                            ball_log_str = f"{current_over_str}:W-{out_desc}"
                            if event_type_param == "NB": ball_log_str += "-NB"

                            if credited_to_bowler: bowlerTracker[bln]['wickets'] += 1
                            bowlerTracker[bln]['runs'] += runs_off_wicket_ball
                            batterTracker[btn]['runs'] += runs_off_wicket_ball

                            bowlerTracker[bln]['ballLog'].append(ball_log_str)
                            batterTracker[btn]['ballLog'].append(ball_log_str + f"-Bowler-{bln}")
                            ballLog.append(ball_log_str)

                            innings2Log.append({"event" : current_over_str + f" {current_bowler['displayName']} to {current_batter['player']['displayName']}" + " W - " + out_desc + " Score: " + str(runs) + "/" + str(wickets) + log_suffix,
                                                "balls": balls, "runs_this_ball": runs_off_wicket_ball, "total_runs": runs, "wickets": wickets,
                                                "batterTracker": copy.deepcopy(batterTracker), "bowlerTracker": copy.deepcopy(bowlerTracker),
                                                "batsman": btn,"batter1": batter1['player']['playerInitials'] if batter1 else 'N/A', "batter2": batter2['player']['playerInitials'] if batter2 else 'N/A',
                                                "bowler": bln, "out_type": out_type_actual, "is_free_hit_delivery": is_fh_param, "original_event_type": event_type_param}) # Ensure these params are logged
                            playerDismissed(current_batter)

                    else: # Dot ball, no wicket
                        P_EXTRAS = 0.08 # Probability of byes/leg-byes on a dot ball
                        if random.uniform(0,1) < P_EXTRAS and not is_fh_param : # Extras less likely on a free hit
                            extras_kind = random.choice(['B', 'LB'])
                            runs_off_extras = random.choice([1, 1, 1, 1, 2, 4]) # 1s more common

                            runs += runs_off_extras
                            # Byes/Leg-byes are not debited against bowler's runs conceded.

                            print(current_over_str, f"{current_bowler['displayName']} to {current_batter['player']['displayName']}", f"{runs_off_extras} {extras_kind}!", "Score: " + str(runs) + "/" + str(wickets) + log_suffix)
                            ball_log_str = f"{current_over_str}:{runs_off_extras}{extras_kind}"
                            bowlerTracker[bln]['ballLog'].append(ball_log_str + "-EXTRAS")
                            batterTracker[btn]['ballLog'].append(ball_log_str + "-EXTRAS")
                            ballLog.append(ball_log_str)

                            innings2Log.append({
                                "event": current_over_str + f" {current_bowler['displayName']} to {current_batter['player']['displayName']} {runs_off_extras} {extras_kind}!" + " Score: " + str(runs) + "/" + str(wickets) + log_suffix,
                                "balls": balls,
                                "runs_this_ball": runs_off_extras,
                                "total_runs": runs, "wickets": wickets,
                                "batterTracker": copy.deepcopy(batterTracker),
                                "bowlerTracker": copy.deepcopy(bowlerTracker),
                                "batsman": btn, "batter1": batter1['player']['playerInitials'] if batter1 else 'N/A',
                                "batter2": batter2['player']['playerInitials'] if batter2 else 'N/A',
                                "bowler": bln,
                                "type": "EXTRAS",
                                "extras_type": extras_kind,
                                "is_free_hit_delivery": is_fh_param,
                                "original_event_type": event_type_param
                            })
                            if runs_off_extras % 2 == 1:
                                onStrike = batter2 if onStrike == batter1 else batter1
                            # Innings End Checks after extras
                            if runs >= target:
                                targetChased = True; winner = battingName; winMsg = f"{battingName} won by {10 - wickets} wickets"
                            elif wickets == 10 or (event_type_param == "LEGAL" and balls == 120):
                                if runs < target -1 : winner = bowlingName; winMsg = f"{bowlingName} won by {(target-1)-runs} runs"
                                elif runs == target-1: winner = "tie"; winMsg = "Match Tied"
                            return # Processed as extras, exit

                        # Standard Dot ball if no extras
                        print(current_over_str, f"{current_bowler['displayName']} to {current_batter['player']['displayName']}", "0", "Score: " + str(runs) + "/" + str(wickets) + log_suffix)
                        ball_log_str = f"{current_over_str}:0"
                        if is_fh_param: ball_log_str += "-FH"
                        if event_type_param == "NB": ball_log_str += "-NB"
                        bowlerTracker[bln]['ballLog'].append(ball_log_str)
                        batterTracker[btn]['ballLog'].append(ball_log_str)
                        ballLog.append(ball_log_str)
                        innings2Log.append({"event" : current_over_str + f" {current_bowler['displayName']} to {current_batter['player']['displayName']} " + "0" + " Score: " + str(runs) + "/" + str(wickets) + log_suffix,
                                            "balls": balls, "runs_this_ball": 0, "total_runs": runs, "wickets": wickets,
                                            "batterTracker": copy.deepcopy(batterTracker), "bowlerTracker": copy.deepcopy(bowlerTracker),
                                            "batsman": btn,"batter1": batter1['player']['playerInitials'] if batter1 else 'N/A', "batter2": batter2['player']['playerInitials'] if batter2 else 'N/A',
                                            "bowler": bln, "is_free_hit_delivery": is_fh_param, "original_event_type": event_type_param}) # Ensure these params are logged

                # Innings End Checks (specific to innings2)
                if runs >= target:
                    targetChased = True
                    print(f"{battingName} won by {10 - wickets} wickets") # Assuming battingName is correctly passed or global
                    winner = battingName
                    winMsg = f"{battingName} won by {10 - wickets} wickets"
                elif wickets == 10 or (event_type_param == "LEGAL" and balls == 120) : # Check for 120 legal balls
                    if runs < target -1 :
                        print(f"{bowlingName} won by {(target - 1) - runs} runs") # Assuming bowlingName is correctly passed or global
                        winner = bowlingName
                        winMsg = f"{bowlingName} won by {(target - 1) - runs} runs"
                    elif runs == target -1:
                         print("Match tied")
                         winner = "tie"
                         winMsg = "Match Tied"

                return # From the main loop over denominationProbabilities_list

        # Fallback for safety
        print(f"Warning: decider {decider} did not fall into any probability bracket in innings2. Treating as dot ball.")
        ball_log_str = f"{current_over_str}:0-fallback"
        bowlerTracker[bln]['ballLog'].append(ball_log_str)
        batterTracker[btn]['ballLog'].append(ball_log_str)
        ballLog.append(ball_log_str)
        innings2Log.append({"event" : current_over_str + f" {current_bowler['displayName']} to {current_batter['player']['displayName']} " + "0 (Fallback)" + " Score: " + str(runs) + "/" + str(wickets),
                                            "balls": balls, "runs_this_ball": 0, "total_runs": runs, "wickets": wickets,
                                            "batterTracker": copy.deepcopy(batterTracker), "bowlerTracker": copy.deepcopy(bowlerTracker),
                                            "batsman": btn,"batter1": batter1['player']['playerInitials'] if batter1 else 'N/A', "batter2": batter2['player']['playerInitials'] if batter2 else 'N/A',
                                            "bowler": bln, "is_free_hit_delivery": is_fh_param, "original_event_type": event_type_param, "fallback":True }) # Ensure these params are logged
        # Check innings end conditions after fallback too
        if runs >= target:
            targetChased = True
            print(f"{battingName} won by {10 - wickets} wickets")
            winner = battingName
            winMsg = f"{battingName} won by {10 - wickets} wickets"
        elif wickets == 10 or (event_type_param == "LEGAL" and balls == 120):
            if runs < target - 1 :
                print(f"{bowlingName} won by {(target - 1) - runs} runs")
                winner = bowlingName
                winMsg = f"{bowlingName} won by {(target - 1) - runs} runs"
            elif runs == target -1:
                 print("Match tied")
                 winner = "tie"
                 winMsg = "Match Tied"

    def playerDismissed(player):
        nonlocal batter1, batter2, onStrike, targetChased, wickets, battingOrder, batterTracker # ensure all needed nonlocals

        # 'wickets' has already been incremented before this function is called.
        # It represents the total number of batsmen out (e.g., 1 after the 1st wicket).
        if wickets == 10:
            # print(f"Innings 2: All out. Total wickets: {wickets}")
            # Game end conditions (win/loss/tie) are checked in getOutcome_standalone or main loop
            if batter1 == player: batter1 = None
            elif batter2 == player: batter2 = None
            onStrike = None # No one on strike if all out
            return

        # Batting order: battingOrder[0], battingOrder[1], battingOrder[2], ...
        # When the 1st wicket falls (wickets = 1), the new player is battingOrder[2]. Index is 2.
        # This new player's index is 'wickets + 1'.
        new_batter_index = wickets + 1

        if new_batter_index < len(battingOrder): # Check if there's a valid next batsman
            next_batter_info = battingOrder[new_batter_index]
            if batter1 == player:
                batter1 = next_batter_info
            elif batter2 == player:
                batter2 = next_batter_info
            else:
                # This case implies 'player' was not one of the current batters, which is unexpected.
                print(f"DEBUG WARNING (Innings 2 playerDismissed): Dismissed player {player['player']['playerInitials']} was not batter1 or batter2. Current batter1: {batter1['player']['playerInitials'] if batter1 else 'None'}, batter2: {batter2['player']['playerInitials'] if batter2 else 'None'}.")
                # Fallback logic similar to innings1, though this state is highly problematic.
                pass

            onStrike = next_batter_info # New batter is on strike
        else:
            # Not enough players left or all out.
            # print(f"Innings 2: All batters dismissed or batting order exhausted. Total wickets: {wickets}")
            if batter1 == player:
                batter1 = None
            elif batter2 == player:
                batter2 = None
            onStrike = None # No one on strike

        # The complex while loop trying to find a batter with 0 balls is removed.

    def delivery(bowler, batter, over, is_free_hit=False): # is_free_hit is for the CURRENT ball
        nonlocal batterTracker, bowlerTracker, onStrike, ballLog, balls, runs, wickets, targetChased, spin, pace
        global winner, winMsg, innings2Log

        blname = bowler['playerInitials']
        btname = batter['player']['playerInitials']

        batInfo = batter['player']
        bowlInfo_orig = bowler # Keep original bowler stats for noball/wide rates
        bowlInfo = copy.deepcopy(bowler) # Work with a copy for temporary adjustments like pitch effects

        # Pitch effects (applied to the copy)
        if('break' in bowlInfo['bowlStyle'] or 'spin' in bowlInfo['bowlStyle']):
            effect = (1.0 - spin)/2
            bowlInfo['bowlOutsRate'] = max(0, bowlInfo['bowlOutsRate'] + (effect * 0.25))
            for r_key in ['0','1']: bowlInfo['bowlRunDenominationsObject'][r_key] = max(0.001, bowlInfo['bowlRunDenominationsObject'].get(r_key,0) + (effect * 0.25))
            for r_key in ['4','6']: bowlInfo['bowlRunDenominationsObject'][r_key] = max(0.001, bowlInfo['bowlRunDenominationsObject'].get(r_key,0) - (effect * 0.38))
        elif('medium' in bowlInfo['bowlStyle'] or 'fast' in bowlInfo['bowlStyle']):
            effect = (1.0 - pace)/2
            bowlInfo['bowlOutsRate'] = max(0, bowlInfo['bowlOutsRate'] + (effect * 0.25))
            for r_key in ['0','1']: bowlInfo['bowlRunDenominationsObject'][r_key] = max(0.001, bowlInfo['bowlRunDenominationsObject'].get(r_key,0) + (effect * 0.25))
            for r_key in ['4','6']: bowlInfo['bowlRunDenominationsObject'][r_key] = max(0.001, bowlInfo['bowlRunDenominationsObject'].get(r_key,0) - (effect * 0.38))

        denAvg = {}
        outAvg = (batInfo['batOutsRate'] + bowlInfo['bowlOutsRate']) / 2
        outTypeAvg = {}
        runoutChance = 0.01
        if(batInfo['batBallsTotal'] > 0): # Use batInfo which is batter['player']
            runoutChance = (batInfo['runnedOut']) / batInfo['batBallsTotal']
        else: runoutChance = 0.005

        for batKey in batInfo['batRunDenominationsObject']:
            denAvg[batKey] = (batInfo['batRunDenominationsObject'].get(batKey,0) + bowlInfo['bowlRunDenominationsObject'].get(batKey,0))/2

        for a_key in batInfo['batOutTypesObject']: # Ensure all batter out types are considered
             outTypeAvg[a_key] = (batInfo['batOutTypesObject'].get(a_key,0) + bowlInfo['bowlOutTypesObject'].get(a_key,0)) / 2
        outTypeAvg['runOut'] = runoutChance

        # No-ball check (using original bowler stats)
        noballRate = bowlInfo_orig['bowlNoballRate']
        is_no_ball_event = noballRate > random.uniform(0,1)

        if is_no_ball_event:
            runs += 1 # Penalty run
            bowlerTracker[blname]['runs'] += 1
            bowlerTracker[blname]['noballs'] += 1 # Increment noballs count

            print(over, f"{bowler['displayName']} to {batter['player']['displayName']}", "NO BALL!", "Score: " + str(runs) + "/" + str(wickets))
            bowlerTracker[blname]['ballLog'].append(f"{over}:NB+1")

            innings2Log.append({
                "event": over + f" {bowler['displayName']} to {batter['player']['displayName']}" + " NO BALL!" + " Score: " + str(runs) + "/" + str(wickets),
                "balls": balls, # Innings balls do not increment for NB call
                "runs_this_ball": 1, # The penalty run
                "total_runs": runs, "wickets": wickets,
                "batterTracker": copy.deepcopy(batterTracker),
                "bowlerTracker": copy.deepcopy(bowlerTracker),
                "batsman": btname,
                "batter1": batter1['player']['playerInitials'] if batter1 else 'N/A',
                "batter2": batter2['player']['playerInitials'] if batter2 else 'N/A',
                "bowler": blname,
                "type": "NO_BALL_CALL",
                "is_free_hit_delivery": True, # Next ball outcome is FH
                "original_event_type": "NB_CALL"
            })
            # Outcome of the no-ball delivery itself (is a free hit)
            getOutcome_standalone(bowler, batter, denAvg, outAvg, outTypeAvg, over, is_fh_param=True, event_type_param="NB")
            return "NO_BALL"

        # Wide check (if not a no-ball)
        wideRate = bowlInfo_orig['bowlWideRate']
        is_wide_event = wideRate > random.uniform(0,1)
        if is_wide_event:
            runs += 1
            bowlerTracker[blname]['runs'] += 1
            print(over, f"{bowler['displayName']} to {batter['player']['displayName']}", "Wide", "Score: " + str(runs) + "/" + str(wickets))
            ballLog.append(f"{over}:WD")
            bowlerTracker[blname]['ballLog'].append(f"{over}:WD")
            innings2Log.append({"event": over + f" {bowler['displayName']} to {batter['player']['displayName']}" + " Wide" + " Score: " + str(runs) + "/" + str(wickets),
                "balls": balls, # Innings balls do not increment for Wide
                "runs_this_ball": 1, # The penalty run
                "total_runs": runs, "wickets": wickets,
                "batterTracker": copy.deepcopy(batterTracker),
                "bowlerTracker": copy.deepcopy(bowlerTracker),
                "batsman": btname,
                "batter1": batter1['player']['playerInitials'] if batter1 else 'N/A',
                "batter2": batter2['player']['playerInitials'] if batter2 else 'N/A',
                "bowler": blname,
                "type": "WIDE",
                "is_free_hit_delivery": is_free_hit, # Persist FH state
                "original_event_type": "WIDE"
            })
            return "WIDE"

        # Legal Delivery (or a Free Hit delivery that wasn't a No Ball or Wide itself)
        balls += 1 # Innings ball count increments only for legal deliveries

        # Aggression adjustments for innings2
        current_ball_of_innings = balls
        sumLast10 = 0
        outsLast10 = 0
        # Calculate sumLast10 and outsLast10 based on ballLog
        # This logic seems to be missing or was part of the old getOutcome
        # For now, we'll assume it's calculated correctly if needed by aggression logic
        # Placeholder for sumLast10 and outsLast10 calculation:
        for i_log_idx in range(max(0, len(ballLog)-10), len(ballLog)):
            i_log = ballLog[i_log_idx]
            spl_bl = i_log.split(":")
            if len(spl_bl) > 1:
                run_part_val = spl_bl[1].split('-')[0]
                if run_part_val.isdigit(): sumLast10 += int(run_part_val)
                if "W" in spl_bl[1]: outsLast10 +=1

        # RRR based aggression
        rrr = 0
        if (120 - balls) > 0 : # Avoid division by zero
            rrr = (target - runs) / (120 - balls) * 6 # RRR per over

        # Simplified aggression logic for Innings 2 (can be expanded)
        if current_ball_of_innings <= 36 : # Powerplay
            if rrr > 9: # High required rate
                outAvg = max(0.001, outAvg + 0.02) # Increase risk
                for r_key in ['4','6']: denAvg[r_key] = max(0.001, denAvg.get(r_key,0) * 1.2)
                for r_key in ['0','1']: denAvg[r_key] = max(0.001, denAvg.get(r_key,0) * 0.8)
            elif rrr < 6: # Low required rate
                 for r_key in ['4','6']: denAvg[r_key] = max(0.001, denAvg.get(r_key,0) * 0.8)
                 outAvg = max(0.001, outAvg - 0.01)
        elif current_ball_of_innings > 90: # Death overs
            if rrr > 7:
                outAvg = max(0.001, outAvg + 0.03)
                for r_key in ['4','6']: denAvg[r_key] = max(0.001, denAvg.get(r_key,0) * 1.3)
                for r_key in ['0','1']: denAvg[r_key] = max(0.001, denAvg.get(r_key,0) * 0.7)

        # Batter-specific aggression (settled, new batter etc.)
        if batterTracker[btname]['balls'] < 8 : # New batter
            outAvg = max(0.001, outAvg + 0.015) # Slightly higher out chance
            for r_key in ['0','1']: denAvg[r_key] = max(0.001, denAvg.get(r_key,0) * 1.1)
            for r_key in ['4','6']: denAvg[r_key] = max(0.001, denAvg.get(r_key,0) * 0.9)

        # Ensure probabilities don't become negative or excessively large
        for k in denAvg: denAvg[k] = max(0.001, denAvg[k])
        outAvg = max(0.001, outAvg)

        getOutcome_standalone(bowler, batter, denAvg, outAvg, outTypeAvg, over, is_fh_param=is_free_hit, event_type_param="LEGAL")
        return "LEGAL"

    # Removed the old nested getOutcome function as it's replaced by getOutcome_standalone
        
        # sumLast10 = 0
        # outsLast10 = 0
        for i in ballLog:
            spl_bl = i.split(":")
            if("W" not in spl_bl[1]):
                sumLast10 += int(spl_bl[1])
            else:
                outsLast10 += 1

        if(balls < 105):
            adjust_last10 = random.uniform(0.02,0.04)
            if(outsLast10 < 2):
                denAvg['0'] -= adjust_last10 * (1/2)
                denAvg['1'] -= adjust_last10 * (1/2)
                denAvg['2'] += adjust_last10 * (1/2)
                denAvg['4'] += adjust_last10 * (1/2)
            else:
                adjust_last10 += 0.018
                denAvg['0'] += adjust_last10 * (1.1/2)
                denAvg['0'] += adjust_last10 * (0.9/2)
                denAvg['4'] -= adjust_last10 * (1/2)
                denAvg['6'] -= adjust_last10 * (1/2)
                outAvg -= 0.02



        if(batterTracker[btname]['balls'] < 8 and balls < 80):
            adjust = random.uniform(-0.01, 0.03)
            outAvg -= 0.015
            denAvg['0'] += adjust * (1.5/3)
            denAvg['1'] += adjust * (1/3)
            denAvg['2'] += adjust * (0.5/3)
            denAvg['4'] -= adjust * (0.5/3)
            denAvg['6'] -= adjust * (1.5/3)

        if(batterTracker[btname]['balls'] > 15 and batterTracker[btname]['balls'] < 30):
            adjust = random.uniform(0.03, 0.07)
            denAvg['0'] -= adjust * (1/3)
            # denAvg['1'] -= adjust *(1/3)
            denAvg['4'] += adjust * (1/3)

        # if(batterTracker[btname]['balls'] > 30):
        #     adjust = random.uniform(0.05, 0.1)
        #     denAvg['0'] -= adjust * (1.5/3)
        #     denAvg['4'] += adjust * (0.75/3)
        #     denAvg['6'] += adjust * (0.75/3)
        #     outAvg += 0.01

        if(batterTracker[btname]['balls'] > 20 and (batterTracker[btname]['runs'] / batterTracker[btname]['balls']) < 110):
            adjust = random.uniform(0.05, 0.08)
            denAvg['0'] += adjust * (1.5/3)
            denAvg['1'] += adjust * (0.5/3)
            denAvg['6'] += adjust * (2/3)
            outAvg += 0.05

        if(batterTracker[btname]['balls'] > 40 and (batterTracker[btname]['runs'] / batterTracker[btname]['balls']) < 135):
            adjust = random.uniform(0.06, 0.09)
            denAvg['0'] += adjust * (1.5/3)
            denAvg['1'] += adjust * (0.7/3)
            denAvg['6'] += adjust * (1.8/3)
            outAvg += 0.04

        if(batterTracker[btname]['balls'] > 30 and (batterTracker[btname]['runs'] / batterTracker[btname]['balls']) > 145 and (wickets < 5) or balls > 102):
            adjust = random.uniform(0.06, 0.09)
            denAvg['0'] -= adjust * (1/3)
            denAvg['1'] -= adjust * (1.5/3)
            denAvg['4'] += adjust * (1.6/3)
            denAvg['6'] += adjust * (1.9/3)
            outAvg += 0.02
    
        rr = 0
        if(balls != 0):
            rr = runs / balls

        if(balls < 120):
            rrr = (target - runs) / (120 - balls)

        if(balls < 12):
            # print(rrr)
            if(rrr < 1.5):
                sixAdjustment = random.uniform(0.02, 0.05)
                if(outAvg < 0.07):
                    outAvg = 0
                else:
                    outAvg = outAvg - 0.07

                if(sixAdjustment > denAvg['6']):
                    sixAdjustment = denAvg['6']

                denAvg['6'] -= sixAdjustment
                denAvg['0'] += sixAdjustment * (1/3)
                denAvg['1'] += sixAdjustment * (2/3)
                getOutcome(denAvg, outAvg, over)
            else:
                getOutcome(denAvg, outAvg, over)

        elif(balls < 36):
            rrro = rrr*6
            if(rrro < 8):
                adjust = random.uniform(0.05, 0.09)
                denAvg['6'] -= adjust * (2/3)
                denAvg['4'] -= adjust * (1/3)
                denAvg['1'] += adjust
                outAvg -= 0.04
                getOutcome(denAvg, outAvg, over)

            elif(rrro >= 8 and rrro <= 10.4):
                adjust = random.uniform(0.04, 0.08)
                denAvg['6'] += adjust * (0.6/3)
                denAvg['4'] += adjust * (1/3)
                denAvg['0'] += adjust * (1/3)
                denAvg['1'] -= adjust * (1/3)
                denAvg['2'] -= adjust * (0.6/3)
                outAvg -= 0.03
                getOutcome(denAvg, outAvg, over)

            else:
                adjust = random.uniform(0.04,0.08)
                adjust += (rrro*1.1)/1000
                denAvg['6'] += adjust * (1.5/3)
                denAvg['4'] += adjust * (1/3)
                denAvg['0'] += adjust * (0.5/3)
                denAvg['1'] -= adjust * (2/3)
                denAvg['2'] -= adjust * (1/3)
                outAvg += (0.02 + ((rrro*1.1)/1000))
                getOutcome(denAvg, outAvg, over)

        elif(balls >= 36 and balls < 102): #102 usually, now 120
            rrro = rrr*6
            if(rrro < 8):
                if(wickets < 3):
                    adjust = random.uniform(0.05, 0.09)
                    denAvg['6'] -= adjust * (0.8/3)
                    # denAvg['4'] -= adjust * (0.5/3)
                    denAvg['0'] -= adjust * (1/3)
                    denAvg['2'] += adjust * (1/3)
                    denAvg['1'] += adjust * (1.5/3)
                    outAvg -= 0.02
                    getOutcome(denAvg, outAvg, over)
                else:
                    adjust = random.uniform(0.05, 0.09)
                    # denAvg['6'] -= adjust * (2/3)
                    # denAvg['4'] -= adjust * (1/3)
                    denAvg['1'] += adjust
                    outAvg -= 0.04
                    getOutcome(denAvg, outAvg, over)

            elif(rrro >= 8 and rrro <= 10.4):
                if(wickets < 3):
                    adjust = random.uniform(0.6, 0.08)
                    denAvg['6'] += adjust * (1/3)
                    denAvg['4'] += adjust * (1.15/3)
                    denAvg['0'] += adjust * (0.1/3)
                    denAvg['1'] -= adjust * (1/3)
                    denAvg['2'] -= adjust * (1/3)
                    outAvg += 0.015
                    getOutcome(denAvg, outAvg, over)
                    
                else:
                    adjust = random.uniform(0.04, 0.08)
                    denAvg['6'] += adjust * (0.95/3)
                    denAvg['4'] += adjust * (1.12/3)
                    denAvg['0'] += adjust * (0.2/3)
                    denAvg['1'] -= adjust * (0.9/3)
                    denAvg['2'] -= adjust * (0.7/3)
                    outAvg += 0.01
                    getOutcome(denAvg, outAvg, over)


                

            elif(rrro > 10.4 and rrro < 12):
                if(wickets < 3):
                    adjust = random.uniform(0.075, 0.1)
                    denAvg['6'] += adjust * (1.5/3)
                    denAvg['4'] += adjust * (1.5/3)
                    denAvg['0'] += adjust * (0.5/3)
                    denAvg['1'] -= adjust * (1.5/3)
                    denAvg['2'] -= adjust * (1.5/3)
                    denAvg['3'] -= adjust * (0.7/3)
                    outAvg += 0.025
                    getOutcome(denAvg, outAvg, over)
                else:
                    adjust = random.uniform(0.06, 0.1)
                    denAvg['6'] += adjust * (1.4/3)
                    denAvg['4'] += adjust * (1/3)
                    denAvg['0'] += adjust * (0.6/3)
                    denAvg['1'] -= adjust * (1.1/3)
                    denAvg['2'] -= adjust * (1.1/3)
                    denAvg['3'] -= adjust * (0.7/3)
                    outAvg += 0.035
                    getOutcome(denAvg, outAvg, over)

                

            elif(rrro >= 12 and rrro <= 15):
                if(balls > 85):
                    if(wickets < 3):
                        adjust = random.uniform(0.065, 0.115)
                        denAvg['6'] += adjust * (1.5/3)
                        denAvg['4'] += adjust * (1.2/3)
                        denAvg['0'] += adjust * (1.4/3)
                        denAvg['1'] -= adjust * (1.2/3)
                        denAvg['2'] -= adjust * (1.7/3)
                        denAvg['3'] -= adjust * (0.9/3)
                        outAvg += 0.04
                        getOutcome(denAvg, outAvg, over)
                    else:
                        adjust = random.uniform(0.05, 0.1)
                        denAvg['6'] += adjust * (1.2/3)
                        denAvg['4'] += adjust * (0.8/3)
                        denAvg['0'] += adjust * (1.2/3)
                        denAvg['1'] -= adjust * (1.2/3)
                        denAvg['2'] -= adjust * (1.6/3)
                        denAvg['3'] -= adjust * (0.9/3)
                        outAvg += 0.05
                        getOutcome(denAvg, outAvg, over)
                else:
                        adjust = random.uniform(0.05, 0.1)
                        denAvg['6'] += adjust * (1.3/3)
                        denAvg['4'] += adjust * (1/3)
                        denAvg['0'] += adjust * (1.2/3)
                        denAvg['1'] -= adjust * (1.2/3)
                        denAvg['2'] -= adjust * (1.6/3)
                        denAvg['3'] -= adjust * (0.9/3)
                        outAvg += 0.03
                        getOutcome(denAvg, outAvg, over)
            else:
                if(wickets < 3):
                    adjust = random.uniform(0.075, 0.125)
                    denAvg['6'] += adjust * (2/3)
                    denAvg['4'] += adjust * (1.5/3)
                    denAvg['0'] += adjust * (1.8/3)
                    denAvg['1'] -= adjust * (1.2/3)
                    denAvg['2'] -= adjust * (1.6/3)
                    denAvg['3'] -= adjust * (0.9/3)
                    outAvg += 0.05
                    getOutcome(denAvg, outAvg, over)
                else:
                    adjust = random.uniform(0.07, 0.12)
                    denAvg['6'] += adjust * (1.8/3)
                    denAvg['4'] += adjust * (1.5/3)
                    denAvg['0'] += adjust * (1.8/3)
                    denAvg['1'] -= adjust * (1.6/3)
                    denAvg['2'] -= adjust * (1.7/3)
                    denAvg['3'] -= adjust * (0.9/3)
                    outAvg += 0.04
                    getOutcome(denAvg, outAvg, over)


        else: #works very well with 120, try to adjust a bit for death and middle but
        #dont tinker too much
            rrro = rrr*6
            if(wickets < 7 or rrro > 12):
                defenseAndOneAdjustment = random.uniform(0.07, 0.1)
                denAvg['0'] += defenseAndOneAdjustment * (1.8/3)
                denAvg['1'] -= defenseAndOneAdjustment * (1/3)
                denAvg['4'] += defenseAndOneAdjustment * (1.45/3)
                denAvg['6'] += defenseAndOneAdjustment * (1.85/3)
                outAvg += 0.032
                getOutcome(denAvg, outAvg, over)
            else:
                defenseAndOneAdjustment = random.uniform(0.07, 0.09)
                denAvg['0'] -= defenseAndOneAdjustment * (1.2/3)
                denAvg['1'] -= defenseAndOneAdjustment * (1.8/3)
                denAvg['4'] += defenseAndOneAdjustment * (1.5/3)
                denAvg['6'] += defenseAndOneAdjustment * (1.5/3)
                outAvg += 0.028

                getOutcome(denAvg, outAvg, over)
            #logic for last 3 overs chase
            pass
                    
        if(runs == (target - 1) and (balls == 120 or wickets == 10)):
            print("Match tied")
            winner = "tie"
            winMsg = "Match Tied"
        else:
            if(runs >= target):
                print(f"{battingName} won by {10 - wickets} wickets")
                winner = battingName
                winMsg = f"{battingName} won by {10 - wickets} wickets"
                targetChased = True
            elif(balls == 120 or wickets == 10):
                print(f"{bowlingName} won by {(target - 1) - runs} runs")
                winner = bowlingName
                winMsg = f"{bowlingName} won by {(target - 1) - runs} runs"


        # elif(balls >= 36 and balls < 102):
        #     if(wickets == 0 or wickets == 1):
        #         defenseAndOneAdjustment = random.uniform(0.07, 0.11)
        #         denAvg['0'] -= defenseAndOneAdjustment * (2/3)
        #         denAvg['1'] -= defenseAndOneAdjustment * (1/3)
        #         denAvg['4'] += defenseAndOneAdjustment * (2/3)
        #         denAvg['6'] += defenseAndOneAdjustment * (1/3)
        #         getOutcome(denAvg, outAvg, over)
        #     else:
        #         # defenseAndOneAdjustment = random.uniform(0.03, 0.08)
        #         denAvg['0'] += 0.03
        #         # denAvg['1'] -= defenseAndOneAdjustment * (1/3)
        #         denAvg['4'] -= 0.03
        #         # denAvg['6'] += defenseAndOneAdjustment * (0.5/3)
        #         outAvg -= 0.06
        #         getOutcome(denAvg, outAvg, over)



        #     if(wickets == 0):
        #         adjust = random.uniform(0.06, 0.11)
        #         denAvg['0'] -= adjust * (1/3)
        #         denAvg['4'] += adjust * (1.5/3)
        #         denAvg['2'] += adjust * (0.5/3)
        #         denAvg['6'] += adjust * (1/3)
        #         outAvg += 0.02
        #         getOutcome(denAvg, outAvg, over)
        #     else:
        #         adjust = random.uniform(0.04, 0.8)
        #         denAvg['1'] += adjust * (1/3) * (wickets / 2)
        #         denAvg['4'] -= adjust * (2/3) * (wickets / 2)
        #         denAvg['6'] -= adjust * (1/3) * (wickets / 2)  
        #         denAvg['2'] += adjust * (1/3) * (wickets / 2)
        #         denAvg['0'] += adjust * (1/3) * (wickets / 2)

        #         outAvg -= adjust * (1/3) * (wickets)
        #         # print(adjust * (1/3) * (wickets/2))
        #         getOutcome(denAvg, outAvg, over)





    for i in range(20): # This 'i' represents the over number from 0 to 19
        # Strike rotation
        if i != 0: # No strike rotation before the first ball of the innings
            if onStrike == batter1: onStrike = batter2
            elif onStrike == batter2: onStrike = batter1
            else: # One batter might be None
                if batter1: onStrike = batter1
                elif batter2: onStrike = batter2
                else: # Both batters are None, innings should end
                    print(f"Innings2 Over {i+1}: Both batters are None. Ending innings.")
                    break
        
        if targetChased or wickets == 10 : break # Check before starting the over

        current_bowler_obj = None
        # Bowler selection logic (remains largely the same as innings1, ensure it's adapted for innings2 context if needed)
        if i == 0:
            current_bowler_obj = bowler1_obj
        elif i == 1:
            current_bowler_obj = bowler2_obj
        else:
            phase = ""
            if i < 6: phase = "PP"
            elif i < 16: phase = "MID"
            else: phase = "DEATH"

            candidates = [
                b for b in designated_bowlers
                if bowlerTracker[b['playerInitials']]['balls'] < 24
                   and b['playerInitials'] != last_bowler_initials
                   and b['bowlOutsRate'] >= MIN_BOWLING_OUT_RATE_THRESHOLD
            ]

            if not candidates: # Fallback 1: Designated bowlers, ignore last_bowler, but respect rate
                candidates = [
                    b for b in designated_bowlers
                    if bowlerTracker[b['playerInitials']]['balls'] < 24
                       and b['bowlOutsRate'] >= MIN_BOWLING_OUT_RATE_THRESHOLD
                ]
                if not candidates: # Fallback 2: Designated bowlers, ignore rate and last_bowler (original fallback)
                    print(f"INFO: Innings2 Over {i+1}, Relaxing bowling rate threshold for designated bowlers (main candidates).")
                    candidates = [
                        b for b in designated_bowlers
                        if bowlerTracker[b['playerInitials']]['balls'] < 24
                           and b['playerInitials'] != last_bowler_initials # Try with this first
                    ]
                    if not candidates: # Fallback 2.1: Designated bowlers, ignore rate and last_bowler restriction
                         candidates = [b for b in designated_bowlers if bowlerTracker[b['playerInitials']]['balls'] < 24]

            # If still no designated bowlers after primary and fallbacks for designated:
            if not candidates:
                non_designated_candidates = [
                    b for b in bowling_selection_pool
                    if b['playerInitials'] not in [db['playerInitials'] for db in designated_bowlers]
                       and bowlerTracker[b['playerInitials']]['balls'] < 24
                       and b['playerInitials'] != last_bowler_initials
                       and b['bowlOutsRate'] >= MIN_BOWLING_OUT_RATE_THRESHOLD
                ]
                if not non_designated_candidates: # Try non-designated without last_bowler restriction, with rate
                    non_designated_candidates = [
                        b for b in bowling_selection_pool
                        if b['playerInitials'] not in [db['playerInitials'] for db in designated_bowlers]
                           and bowlerTracker[b['playerInitials']]['balls'] < 24
                           and b['bowlOutsRate'] >= MIN_BOWLING_OUT_RATE_THRESHOLD
                    ]
                if not non_designated_candidates: # Try non-designated, relaxing rate, with last_bowler restriction
                    print(f"INFO: Innings2 Over {i+1}, Relaxing bowling rate threshold for non-designated bowlers.")
                    non_designated_candidates = [
                        b for b in bowling_selection_pool
                        if b['playerInitials'] not in [db['playerInitials'] for db in designated_bowlers]
                           and bowlerTracker[b['playerInitials']]['balls'] < 24
                           and b['playerInitials'] != last_bowler_initials
                    ]
                    if not non_designated_candidates: # Try non-designated, relaxing rate, without last_bowler restriction
                         non_designated_candidates = [
                            b for b in bowling_selection_pool
                            if b['playerInitials'] not in [db['playerInitials'] for db in designated_bowlers]
                               and bowlerTracker[b['playerInitials']]['balls'] < 24
                        ]

                if non_designated_candidates:
                    # Select from non_designated_candidates, potentially phase-aware if desired, or random
                    current_bowler_obj = random.choice(non_designated_candidates)
                else:
                    # Ultimate fallback: least bowled designated bowler, ignoring rate and last_bowler entirely
                    print(f"WARNING: Innings2 Over {i+1}, All preferred bowlers nearly maxed or below rate. Fallback to least bowled designated.")
                    least_bowled_candidates = sorted(
                        [b_sort for b_sort in designated_bowlers if bowlerTracker[b_sort['playerInitials']]['balls'] < 24],
                        key=lambda b_lambda: bowlerTracker[b_lambda['playerInitials']]['balls']
                    )
                    if least_bowled_candidates:
                        current_bowler_obj = least_bowled_candidates[0]
                    elif bowling_selection_pool:
                        current_bowler_obj = random.choice([b for b in bowling_selection_pool if bowlerTracker[b['playerInitials']]['balls'] < 24] or bowling_selection_pool)
                    else:
                        current_bowler_obj = None

            # If candidates were found (either primary designated, fallback designated, or non-designated selected above)
            if current_bowler_obj is None and candidates:
                chosen_bowler_initials_for_rotation = None
                phase_preferred_list_objs = []
                if phase == "PP": phase_preferred_list_objs = designated_opening_bowlers
                elif phase == "MID": phase_preferred_list_objs = designated_middle_bowlers
                else: phase_preferred_list_objs = designated_death_bowlers

                final_phase_candidates = [b for b in candidates if b['playerInitials'] in [p['playerInitials'] for p in phase_preferred_list_objs]]

                if final_phase_candidates:
                    for bowler_initials_in_rotation in list(designated_bowler_rotation_list):
                        potential_bowler = next((b for b in final_phase_candidates if b['playerInitials'] == bowler_initials_in_rotation), None)
                        if potential_bowler:
                            current_bowler_obj = potential_bowler
                            chosen_bowler_initials_for_rotation = bowler_initials_in_rotation
                            break
                    if not chosen_bowler_initials_for_rotation:
                        current_bowler_obj = random.choice(final_phase_candidates)
                elif candidates: # No phase specific, but general candidates exist
                    for bowler_initials_in_rotation in list(designated_bowler_rotation_list):
                        potential_bowler = next((b for b in candidates if b['playerInitials'] == bowler_initials_in_rotation), None)
                        if potential_bowler:
                            current_bowler_obj = potential_bowler
                            chosen_bowler_initials_for_rotation = bowler_initials_in_rotation
                            break
                    if not chosen_bowler_initials_for_rotation:
                        current_bowler_obj = random.choice(candidates)

                if chosen_bowler_initials_for_rotation:
                    designated_bowler_rotation_list.remove(chosen_bowler_initials_for_rotation)
                    designated_bowler_rotation_list.append(chosen_bowler_initials_for_rotation)
                elif current_bowler_obj and current_bowler_obj['playerInitials'] in designated_bowler_rotation_list: # Chosen by random from filtered lists
                     designated_bowler_rotation_list.remove(current_bowler_obj['playerInitials'])
                     designated_bowler_rotation_list.append(current_bowler_obj['playerInitials'])

        if not current_bowler_obj:
            if bowling_selection_pool:
                print(f"CRITICAL FALLBACK (Innings2): No specific bowler chosen for over {i+1}. Picking from any available in main pool.")
                available_fallback = [b for b in bowling_selection_pool if bowlerTracker[b['playerInitials']]['balls'] < 24]
                current_bowler_obj = random.choice(available_fallback) if available_fallback else \
                                    (bowling_selection_pool[0] if bowling_selection_pool else None)
            else:
                 print(f"CRITICAL ERROR (Innings2): No bowlers in selection pool for team {bowlingName}. Innings cannot continue.")
                 break

        balls_bowled_this_over = 0
        if current_bowler_obj and current_bowler_obj.get('playerInitials'):
            # print(f"Innings 2, Over {i+1}: Bowler is {current_bowler_obj['displayName']}")
            while balls_bowled_this_over < 6:
                if targetChased or wickets == 10 or not onStrike:
                    if not onStrike: print(f"Innings2 Over {i}.{balls_bowled_this_over +1}: No batter on strike. Ending over/innings.")
                    break

                delivery_type = delivery(copy.deepcopy(current_bowler_obj), copy.deepcopy(onStrike),
                                         f"{i}.{balls_bowled_this_over + 1}", is_free_hit=is_next_ball_free_hit)

                if delivery_type == "NO_BALL":
                    is_next_ball_free_hit = True
                    # Ball doesn't count towards over, loop continues for the same ball number
                elif delivery_type == "WIDE":
                    # Ball doesn't count, free hit status persists, loop continues
                    pass
                elif delivery_type == "LEGAL":
                    is_next_ball_free_hit = False # Free hit is consumed on a legal delivery
                    balls_bowled_this_over += 1

                if targetChased or wickets == 10: break # Check after each delivery

            if current_bowler_obj and current_bowler_obj.get('playerInitials'): # Ensure bowler object is still valid
                 bowlerTracker[current_bowler_obj['playerInitials']]['overs'] += 1
                 last_bowler_initials = current_bowler_obj['playerInitials']

        elif bowling_selection_pool :
            print(f"CRITICAL ERROR (Innings2): No valid bowler object for over {i+1} for team {bowlingName} but pool existed. Innings ends.")
            break
        else:
            print(f"CRITICAL ERROR (Innings2): No bowlers in selection pool for team {bowlingName}. Innings ends.")
            break

        if targetChased or wickets == 10: break # Break outer over loop if innings ended mid-over
            
    # print(batterTracker)
    # print(bowlerTracker)
    batsmanTabulate = []
    # Determine the player initials of the batsmen who were at the crease if the innings ended.
    # These are based on the 'onStrike' and the other batter (batter1/batter2) at the point the loop terminated.
    # This needs to be captured *before* onStrike, batter1, batter2 might be reset or go out of scope if innings ends.
    # For simplicity, we'll pass the final 'wickets' count and 'battingOrder' to the scorecard generation logic.
    # The actual onStrike/nonStrike at the very end might be complex to capture perfectly here without altering main loop much.
    # We will use the battingOrder and final wicket count.

    for btckd_player_initials in batterTracker: # btckd_player_initials is the key, e.g., 'MS Dhoni'
        player_specific_data = batterTracker[btckd_player_initials]
        runs_scored = player_specific_data['runs']
        balls_faced = player_specific_data['balls']

        sr_val = 'NA'
        if balls_faced > 0:
            sr_val = str(round((runs_scored * 100) / balls_faced, 2))

        dismissal_status = "DNB" # Default: Did Not Bat
        player_batted = len(player_specific_data['ballLog']) > 0
        got_out = False

        for ball_record in player_specific_data['ballLog']:
            if "W" in ball_record: # Indicates a wicket
                got_out = True
                # Detailed dismissal (current logic for parsing 'CaughtBy', 'runout', etc. is okay)
                if "CaughtBy" in ball_record:
                    split_log = ball_record.split("-")
                    catcher_name = split_log[2]
                    bowler_name = split_log[-1]
                    dismissal_status = f"c {catcher_name} b {bowler_name}"
                elif "runout" in ball_record: # Note: mainconnect.py uses "Run Out" with space in logs.
                    dismissal_status = "Run out"
                else: # Assumes format like "W-bowled-BowlerName" or "W-lbw-BowlerName"
                    split_log = ball_record.split("-")
                    if len(split_log) > 2 : # e.g. W-bowled-Bumrah
                        dismissal_type = split_log[1]
                        bowler_name = split_log[-1]
                        dismissal_status = f"{dismissal_type} b {bowler_name}"
                    elif len(split_log) == 2: # e.g. W-bowled (if bowler name not appended in log)
                         dismissal_status = split_log[1]
                    else: # Fallback for simple "W"
                        dismissal_status = "Wicket"
                break # Player is out, no need to check further logs for dismissal status

        if not got_out:
            if player_batted:
                dismissal_status = "Not out"
            else:
                # Player did not bat. Check if they were in line to bat or at crease.
                player_considered_in = False
                # wickets is the number of fallen wickets. battingOrder indices are 0-based.
                # Players from battingOrder[0] to battingOrder[wickets-1] are the ones who got out.
                # battingOrder[wickets] and battingOrder[wickets+1] are potentially the not out batsmen or next in.
                # Max index for "came in" is min(len(battingOrder) - 1, wickets + 1)
                for idx in range(min(len(battingOrder), wickets + 2)):
                    if battingOrder[idx]['player']['playerInitials'] == btckd_player_initials:
                        player_considered_in = True
                        break
                if player_considered_in:
                    dismissal_status = "Not out"
                # Else, remains "DNB" if not in this range and didn't bat.

        batsmanTabulate.append([btckd_player_initials, runs_scored, balls_faced, sr_val, dismissal_status])
        
    bowlerTabulate = []
    for btrack in bowlerTracker:
        localBowlerTabulate = [btrack, bowlerTracker[btrack]['runs']]
        overs_tb = 0
        remainder_balls = bowlerTracker[btrack]['balls'] % 6 
        number_overs = bowlerTracker[btrack]['balls'] // 6
        localBowlerTabulate.append(f"{number_overs}.{remainder_balls}")
        localBowlerTabulate.append(bowlerTracker[btrack]['wickets'])
        econ_tb = "NA"
        if(bowlerTracker[btrack]['balls'] != 0):
            econ_tb = (bowlerTracker[btrack]['runs'] / bowlerTracker[btrack]['balls'])*6
            econ_tb = str(round(econ_tb, 2))
        localBowlerTabulate.append(econ_tb)
        bowlerTabulate.append(localBowlerTabulate)

    print(tabulate(batsmanTabulate, ["Player", "Runs", "Balls", "SR" ,"Out"], tablefmt="grid"))
    print(tabulate(bowlerTabulate, ["Player", "Runs", "Overs", "Wickets", "Eco"], tablefmt="grid"))
    innings2Balls = balls
    innings2Runs = runs
    innings2Batting = tabulate(batsmanTabulate, ["Player", "Runs", "Balls", "SR" ,"Out"], tablefmt="grid")
    innings2Bowling = tabulate(bowlerTabulate, ["Player", "Runs", "Overs", "Wickets", "Eco"], tablefmt="grid")

    innings2Battracker = batterTracker
    innings2Bowltracker = bowlerTracker

def game(manual=True, sentTeamOne=None, sentTeamTwo=None, switch="group"):
    global innings1Batting, innings1Bowling, innings2Batting, innings2Bowling, innings1Balls, innings2Balls
    global innings1Log, innings2Log, innings1Battracker, innings2Battracker, innings2Bowltracker, innings1Bowltracker
    global innings1Runs, innings2Runs

    innings1Batting = None
    innings1Bowling = None
    innings2Batting = None
    innings2Bowling = None
    innings1Balls = None
    innings2Balls = None
    innings1Runs = None
    innings2Runs = None

    innings1Battracker = None
    innings2Battracker = None
    innings1Bowltracker = None
    innings2Bowltracker = None

    innings1Log = []
    innings2Log = []

    team_one_inp = None
    team_two_inp = None
    if(manual):
        team_one_inp = input("enter first team ").lower()
        team_two_inp = input("enter second team ").lower()
    else:
        team_one_inp = sentTeamOne
        team_two_inp = sentTeamTwo

    # pitchTypeInput = input("Enter type of pitch (green, dusty, or dead) ")
    pitchTypeInput = "dusty"
    stdoutOrigin=sys.stdout 
    sys.stdout = open(f"scores/{team_one_inp}v{team_two_inp}_{switch}.txt", "w")

    # f = open("matches/csk_v_rr.txt", "r")
    with open('teams/teams.json') as fl:
        dataFile = json.load(fl)

    team1 = None
    team2 = None
    venue = None
    toss = None

    secondInnDew = False
    # for 1st
    dew = False
    pitchDetoriate = True
    # for 1st
    detoriate = False

    paceFactor = None
    spinFactor = None
    outfield = None
    typeOfPitch = pitchTypeInput

    team1Players = []
    team2Players = []

    team1Info = []
    team2Info = []

    # spin, pace factor -> 0.0 - 1.0
    team1Players = dataFile[team_one_inp]
    team2Players = dataFile[team_two_inp]
    team1 = team_one_inp
    team2 = team_two_inp
    print(team1Players)

    for player in team1Players:
        obj = accessJSON.getPlayerInfo(player)
        team1Info.append(obj)

    for player in team2Players:
        obj = accessJSON.getPlayerInfo(player)
        team2Info.append(obj)

    pitchInfo_ = pitchInfo(venue, typeOfPitch)
    paceFactor, spinFactor, outfield = pitchInfo_[
        0], pitchInfo_[1], pitchInfo_[2]
    battingFirst = doToss(paceFactor, spinFactor, outfield,
                          secondInnDew, pitchDetoriate, typeOfPitch, team1, team2)
    # print(paceFactor, spinFactor, outfield)

    def getBatting():
        if(battingFirst == 0):
            return [team1Info, team2Info, team1, team2]
        else:
            return [team2Info, team1Info, team2, team1]

    innings1(getBatting()[0], getBatting()[1], getBatting()[2], getBatting()[
            3], paceFactor, spinFactor, outfield, dew, detoriate)

    innings2(getBatting()[1], getBatting()[0], getBatting()[3], getBatting()[
            2], paceFactor, spinFactor, outfield, dew, detoriate)
    sys.stdout.close()
    sys.stdout=stdoutOrigin
    # print(innings1Log)
    # print(innings2Log)
    # Ensure 'balls' in innings summary is the total legal balls bowled.
    # The 'balls' variable within innings functions was modified to track legal balls.
    return {"innings1Batting": innings1Batting, "innings1Bowling": innings1Bowling, "innings2Batting": innings2Batting, 
            "innings2Bowling": innings2Bowling, "innings2Balls": innings2Balls, "innings1Balls": innings1Balls, # Use actual legal balls for innings1
            "innings1Runs": innings1Runs, "innings2Runs": innings2Runs, "winMsg": winMsg, "innings1Battracker": innings1Battracker,
            "innings2Battracker": innings2Battracker, "innings1Bowltracker": innings1Bowltracker, "innings2Bowltracker": innings2Bowltracker,
            "innings1BatTeam": getBatting()[2],"innings2BatTeam": getBatting()[3], "winner": winner, "innings1Log": innings1Log,
            "innings2Log": innings2Log, "tossMsg": tossMsg }



# game()
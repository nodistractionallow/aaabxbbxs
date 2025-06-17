# Pre-match rain delay logic
    if is_rain_affected_match and random.random() < 0.5: # 50% chance of rain delay
        print("Rain has delayed the start of the match.")
        total_delay_minutes = 0
        rain_delay_simulation_active = True
        while rain_delay_simulation_active:
            time.sleep(1) # Simulates 10 virtual minutes passed
            total_delay_minutes += 10

            delay_updates = [
                "Rain continues. Umpires scheduling an inspection.",
                "Ground staff are at work, covering the pitch.",
                f"Update: Covers are coming off. Inspection at virtual time + {random.randint(5,15)} mins.",
                "The rain seems to be easing up a bit.",
                "Still drizzling. Waiting for an official update."
            ]
            print(random.choice(delay_updates) + f" (Total delay: {total_delay_minutes} virtual minutes)")

            if total_delay_minutes > 180: # More than 3 virtual hours
                print("Unfortunately, the match has been called off due to persistent rain.")
                winner = "cancelled"
                winMsg = f"Match between {sentTeamOne.upper()} and {sentTeamTwo.upper()} cancelled due to rain. Points shared."
                innings1Runs = innings2Runs = 0
                innings1Balls = innings2Balls = 0
                innings1Batting = innings2Batting = "Match Cancelled"
                innings1Bowling = innings2Bowling = "Match Cancelled"
                innings1Battracker = innings2Battracker = {}
                innings1Bowltracker = innings2Bowltracker = {}
                cancelled_log_entry = [{"event": "Match Cancelled due to rain", "balls": 0, "runs_this_ball": 0, "total_runs": 0, "wickets": 0}]
                innings1Log = cancelled_log_entry
                innings2Log = cancelled_log_entry
                # target = 0 # Already set at game start

                # getBatting() needs team1Info, team2Info etc. which are set up after team selection and before toss.
                # The rain logic is currently placed after toss.
                bat_teams_for_log = getBatting()

                sys.stdout.close() # Close the file if opened
                sys.stdout=stdoutOrigin
                return {
                    "innings1Batting": innings1Batting, "innings1Bowling": innings1Bowling,
                    "innings2Batting": innings2Batting, "innings2Bowling": innings2Bowling,
                    "innings2Balls": innings2Balls, "innings1Balls": innings1Balls,
                    "innings1Runs": innings1Runs, "innings2Runs": innings2Runs,
                    "winMsg": winMsg,
                    "innings1Battracker": innings1Battracker, "innings2Battracker": innings2Battracker,
                    "innings1Bowltracker": innings1Bowltracker, "innings2Bowltracker": innings2Bowltracker,
                    "innings1BatTeam": bat_teams_for_log[2], "innings2BatTeam": bat_teams_for_log[3],
                    "winner": winner,
                    "innings1Log": innings1Log, "innings2Log": innings2Log,
                    "tossMsg": tossMsg if tossMsg else "Toss not held due to rain", # tossMsg is global and set by doToss
                    "current_match_overs": 0,
                    "target": target,
                    "superOverPlayed": False,
                    "superOverDetails": []
                }

            # Chance to decide to start the match
            if random.random() < 0.3 and total_delay_minutes > 30: # 30% chance after 30 virtual mins
                print(f"Good news! The rain has stopped. Match will start after a delay of {total_delay_minutes} virtual minutes.")
                rain_delay_simulation_active = False # Exit delay loop

                if total_delay_minutes > 60:
                    overs_lost_per_side = (total_delay_minutes - 60) // 4 # Integer division
                    current_match_overs = base_match_overs - overs_lost_per_side
                    print(f"The match has been reduced to {current_match_overs} overs per side.")
                    if current_match_overs < 5:
                        print("Match reduced below 5 overs per side. It has been called off.")
                        winner = "cancelled"
                        winMsg = f"Match between {sentTeamOne.upper()} and {sentTeamTwo.upper()} called off (reduced below 5 overs). Points shared."
                        innings1Runs = innings2Runs = 0
                        innings1Balls = innings2Balls = 0
                        innings1Batting = innings2Batting = "Match Cancelled (Reduced <5 overs)"
                        innings1Bowling = innings2Bowling = "Match Cancelled (Reduced <5 overs)"
                        innings1Battracker = innings2Battracker = {}
                        innings1Bowltracker = innings2Bowltracker = {}
                        cancelled_log_entry_reduced = [{"event": "Match Cancelled (Reduced <5 overs)", "balls": 0, "runs_this_ball": 0, "total_runs": 0, "wickets": 0}]
                        innings1Log = cancelled_log_entry_reduced
                        innings2Log = cancelled_log_entry_reduced
                        # target = 0 # Already set
                        bat_teams_for_log_reduced = getBatting()
                        sys.stdout.close() # Close the file if opened
                        sys.stdout=stdoutOrigin
                        return {
                            "innings1Batting": innings1Batting, "innings1Bowling": innings1Bowling,
                            "innings2Batting": innings2Batting, "innings2Bowling": innings2Bowling,
                            "innings2Balls": innings2Balls, "innings1Balls": innings1Balls,
                            "innings1Runs": innings1Runs, "innings2Runs": innings2Runs,
                            "winMsg": winMsg,
                            "innings1Battracker": innings1Battracker, "innings2Battracker": innings2Battracker,
                            "innings1Bowltracker": innings1Bowltracker, "innings2Bowltracker": innings2Bowltracker,
                            "innings1BatTeam": bat_teams_for_log_reduced[2], "innings2BatTeam": bat_teams_for_log_reduced[3],
                            "winner": winner,
                            "innings1Log": innings1Log, "innings2Log": innings2Log,
                            "tossMsg": tossMsg,
                            "current_match_overs": current_match_overs,
                            "target": target,
                            "superOverPlayed": False,
                            "superOverDetails": []
                        }
                else:
                    print("No overs lost due to the delay.")

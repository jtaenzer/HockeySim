import random, copy
from team_info import team_info

class schedule_maker:

    def __init__(self, league, teams, ngames, infile="", fileformat="csv"):
        self.league     = league
        self.teams      = teams
        self.Ngames     = ngames
        self.infile     = infile
        self.fileformat = fileformat

        self.schedule = dict()

        # If an input file was specified, automatically read the schedule from it
        if self.infile:
            if self.fileformat is "csv":
                self.schedule = self.import_schedule_csv()
            else:
                print("File format %s is not supported" % self.fileformat)

        else:
            print("No schedule file specified, generating a random schedule")
            self.schedule = self.generate_schedule_simple()

    # Imports a csv formatted schedule
    # Now records visitor and home for each game for tie-break purposes
    def import_schedule_csv(self):

        print("")
        print("importing schedule from : %s" % self.infile)
        print("")

        build_schedule = {}
        game_counter = 0
        # Read schedule from file
        sched_file = open(self.infile, "r")
        for line in sched_file:
            line_split = line.replace("\n", "").split(',')
            if line_split[0] == "Date":
                continue
            sched_key = "game" + str(game_counter)
            build_schedule[sched_key] = {"date": line_split[0],
                                         "visitor": line_split[1], "visitor_goals": line_split[2],
                                         "home": line_split[3], "home_goals": line_split[4],
                                         "OT": line_split[5]}

            if build_schedule[sched_key]["visitor_goals"] and build_schedule[sched_key]["home_goals"]:
                v_goals = int(build_schedule[sched_key]["visitor_goals"])
                h_goals = int(build_schedule[sched_key]["home_goals"])
                winner = build_schedule[sched_key]["visitor"] if v_goals > h_goals else build_schedule[sched_key]["home"]
            else:
                winner = ""
            build_schedule[sched_key].update({"winner": winner})



            game_counter += 1

        if not self.chk_schedule_simple(build_schedule):
            print("Imported schedule failed sanity check.")
            return dict()

        return build_schedule

    # Generate a random schedule where every team in teams will play N games
    # Missing rules:
    # 1. Balancing home/away games
    # 2a. Ensuring each team plays each other team the same number of times
    # 2b. Ensuring each team plays each other team the correct number of times (based on divisional/conference rules)
    # ...Probably more
    # This should only be used for debugging in its current state
    def generate_schedule_simple(self):
        build_schedule = {}
        extra = ""  # extra is used to keep track of teams that have an "extra" game due to an uneven number of teams
        gamecounter = 0
        daycounter = 0

        # Loop until the generated schedule has Ngames games for every team
        while not self.chk_schedule_simple(build_schedule):
            key = "game"+str(gamecounter)  # key for the schedule dictionary

        # Deepcopy teams so we can remove entries without affecting the original list
            teams_local = copy.deepcopy(self.teams)

            # If extra is non-empty, we generated a remainder game in the previous iteration
            # so we remove the team that played an extra game from teams_local
            if extra:
                teams_local.remove(extra)
                extra = ""

            # Add games to schedule by choosing teams at random from teams_remaining
            # Teams chosen for games are removed from teams_remaining until at most 1 is left
            teams_remaining = copy.deepcopy(teams_local)
            while len(teams_remaining) > 1:
                home = random.choice(teams_remaining)
                teams_remaining.remove(home)
                away = random.choice(teams_remaining)
                teams_remaining.remove(away)
                build_schedule[key] = {"date": "day"+str(daycounter), "visitor": away.name, "home": home.name}
                gamecounter += 1

        # If len(teams) is odd, we will have a "remainder" team that didn't get a game scheduled in the above while loop
        # Schedule a game for that team with  another random team
        # The team with an "extra" game will be removed from teams_local / teams_remaining in the next loop iteration
            if len(teams_remaining) > 0:
                daycounter += 1
                remainder = teams_remaining[0]
                teams_local.remove(remainder)
                extra = random.choice(teams_local)
                teams_remaining.append(extra)
                home = random.choice(teams_remaining)
                teams_remaining.remove(home)
                away = random.choice(teams_remaining)
                teams_remaining.remove(away)
                build_schedule[key] = {"date": "day"+str(daycounter), "visitor": away.name, "home": home.name}
                gamecounter += 1

        return build_schedule

    # Adapting for the new dictionary structure of the schedule
    def chk_schedule_simple(self, build_schedule):

        # If schedule is empty, return False
        if not build_schedule:
            return False

        # Regenerating this dictionary every time isn't efficiency -- rethink
        team_game_counter = dict()
        for team in self.teams:
            team_game_counter[team.name] = 0

        # Count how many games each team plays in the current schedule
        for game in build_schedule:
            for team in self.teams:
                if team.name in build_schedule[game]["visitor"] or team.name in build_schedule[game]["home"]:
                    team_game_counter[team.name] += 1

        # If any team doesn't have Ngames scheduled, return False
        for team in self.teams:
            if team_game_counter[team.name] != self.Ngames:
                return False

            # If we survived the previous for loop, it should be safe to return True
        return True

import random, copy
from team_info import team_info

class play_season:

    def __init__(self, teams, schedule, start):
        self.teams           = teams
        self.schedule        = schedule
        self.game_record     = copy.deepcopy(self.schedule)
        self.standings       = self.generate_initial_standings_NHL(self.teams)

        # Warning that there is no real protection against "bad" start values at present...
        if start == "auto":
            self.start = self.find_first_unplayed_game()
        else:
            self.start = int(start)

    # Run through the schedule and decide each game with a coin flip
    # Ideas/thoughts:
    # -Use a weighted coin flip instead, take weights for each team as an input
    # -Modify the initial weight based on each teams record
    #  Doing this in a simple way will be susceptible to fluctuations, how to avoid that? Cap the weight at some value?
    # -There should be a better way to do the entries to the standings dictionary...
    def play_games_simple(self, allowOT=True):
        #for day in self.game_record:
        for i in xrange(len(self.game_record)):
            sched_key = "game"+str(i)
            if i < self.start:
                continue
            else:
                game = [self.schedule[sched_key]["visitor"], self.schedule[sched_key]["home"]]
                winner = random.choice(game)
                OT = self.overtime_check() if allowOT else ""
                self.game_record[sched_key].update({"winner": winner})
                self.game_record[sched_key].update({'OT': OT})

        self.standings = self.generate_standings_from_game_record(self.teams, self.game_record)

    def find_first_unplayed_game(self):
        for i in xrange(len(self.schedule)):
            game="game"+str(i)
            if not self.schedule[game]["visitor_goals"] and not self.schedule[game]["home_goals"]:
                return i
        else:
            return 0

    # Decide if a game went to overtime assuming 25% of games go to OT
    def overtime_check(self):
        result = random.randint(0, 100)
        # Approximate numbers stolen from an article about 3on3 OT
        # Regulation - 75%, OT - 15%, SO - 10%
        if result >= 90:
            return "SO"
        elif result < 90 and result >= 75:
            return "OT"
        else:
            return ""

    # Determine which teams made the playoffs based on the NHL wildcard format
    # Tie-breaking based on ROW is implemented
    # Tie-breaking based on head-to-head games and goals scored not implemented. Not clear how to do this yet.
    def determine_playoffs_NHL(self, result):

        # Should these by hard coded??
        Nteams = 16  # number of teams that can make the playoffs
        div_cutoff = 3  # top 3 teams from each division automatically make the playoffs
        wildcard_cutoff = 2  # The top 2 teams from each conference that didn't get a div spot take the wildcard spots

        atlantic, metro, central, pacific = self.sort_standings_by_division_NHL(self.standings)
        east = self.merge_dicts(atlantic, metro)
        west = self.merge_dicts(central, pacific)

        #standings_sorted = chk_tiebreaks(self.game_record, sort_by_points_row(self.standings))
        atlantic_sorted = self.chk_tiebreaks_NHL(self.sort_by_points_row(atlantic))
        metro_sorted = self.chk_tiebreaks_NHL(self.sort_by_points_row(metro))
        central_sorted = self.chk_tiebreaks_NHL(self.sort_by_points_row(central))
        pacific_sorted = self.chk_tiebreaks_NHL(self.sort_by_points_row(pacific))

        for i in xrange(div_cutoff):
            result[atlantic_sorted[i][0]] += 1
            result[metro_sorted[i][0]] += 1
            east.pop(atlantic_sorted[i][0])
            east.pop(metro_sorted[i][0])
            result[central_sorted[i][0]] += 1
            result[pacific_sorted[i][0]] += 1
            west.pop(central_sorted[i][0])
            west.pop(pacific_sorted[i][0])

        east_sorted = self.chk_tiebreaks_NHL(self.sort_by_points_row(east))
        west_sorted = self.chk_tiebreaks_NHL(self.sort_by_points_row(west))

        for i in xrange(wildcard_cutoff):
            result[east_sorted[i][0]] += 1
            result[west_sorted[i][0]] += 1

    # This method checks for ties and re-orders the standings based on tie-breakers
    # For now only the head-to-head record is checked
    def chk_tiebreaks_NHL(self, standings_sorted):
        checkedpairs = []
        for i in xrange(len(standings_sorted)):
            for j in xrange(len(standings_sorted)):
                if i == j:
                    continue
                if [i, j] in checkedpairs or [j, i] in checkedpairs:
                    continue
                if standings_sorted[i][1]["points"] == standings_sorted[j][1]["points"] and standings_sorted[i][1][
                   "ROW"] == standings_sorted[j][1]["ROW"]:
                    if self.chk_head_to_head_NHL(standings_sorted[i][0], standings_sorted[j][0]) == standings_sorted[j][0]:
                        standings_sorted = self.swap_tuple_elements(standings_sorted, i, j)
                checkedpairs.append([i, j])
        return standings_sorted

    # Check the head to head record for tie breaking
    # Rules (per NHL.com):
    # Team with that earned the most points in games between the two teams wins the tie-break
    # When the teams played an odd number of games, points earned in the first game played in the city that had
    # the extra game shall not be included.
    # The last fallback if the teams are still tied is the team with the greater goal differential -- not clear what
    # to do there, just return random for now
    def chk_head_to_head_NHL(self, team1, team2):

        # First for convenience find the head-to-head games in our self.game_record and put them in a smaller dictionary
        head_to_head = dict()
        for game in self.game_record:
            if (self.game_record[game]["home"] == team1 or self.game_record[game]["visitor"] == team1) and \
               (self.game_record[game]["home"] == team2 or self.game_record[game]["visitor"] == team2):
                head_to_head[game] = (self.game_record[game])

        # For odd numbers of games, determine which team had more home games and
        # "pop" their first home game from head_to_head
        # This could probably be improved
        if len(head_to_head) % 2 != 0:
            count = {team1: 0, team2: 0}
            head_to_head_sorted = sorted(head_to_head.items(), key=lambda kv: kv[1]['date'])
            for i in xrange(len(head_to_head_sorted)): count[head_to_head_sorted[i][1]["home"]] += 1
            if count[team1] > count[team2]:
                pop_team = team1
            else:
                pop_team = team2
            for i in xrange(len(head_to_head_sorted)):
                if count[head_to_head_sorted[i][1]["home"]] == pop_team:
                    head_to_head.pop(head_to_head_sorted[i][0])

        # Determine how many points each team earned in their games against each other
        team1_pts = 0
        team2_pts = 0
        for game in head_to_head:
            if self.game_record[game]["winner"] == team1:
                team1_pts += 2
                if self.game_record[game]["OT"] == "OT" or self.game_record[game]["OT"] == "SO":
                    team2_pts += 1
            elif self.game_record[game]["winner"] == team2:
                team2_pts += 2
                if self.game_record[game]["OT"] == "OT" or self.game_record[game]["OT"] == "SO":
                    team1_pts += 1

        if team1_pts > team2_pts:
            return team1
        elif team2_pts < team1_pts:
            return team2
        else:
            return random.choice([team1, team2])  # If they're still tied, just return a random choice

    # Sort the standings by NHL divisions
    # Used in determine_playoffs_simple_NHL()
    @staticmethod
    def sort_standings_by_division_NHL(standings):
        atlantic = dict()
        metro    = dict()
        central  = dict()
        pacific  = dict()

        for team in standings:
            if standings[team]['div'] == 'a':
                atlantic[team] = standings[team]
            elif standings[team]['div'] == 'm':
                metro[team] = standings[team]
            elif standings[team]['div'] == 'c':
                central[team] = standings[team]
            elif standings[team]['div'] == 'p':
                pacific[team] = standings[team]

        return atlantic, metro, central, pacific

    # Prints the standings in a nicely formatted way
    # Currently gets called to print initial standings when starting a sim mid-season
    @staticmethod
    def print_standings_sorted(standings, format = "league"):

        print '{:<25}'.format('Team'), \
              '{:<10}'.format('Wins'), \
              '{:<10}'.format('Losses'), \
              '{:<10}'.format('OT Losses'), \
              '{:<10}'.format('Points'), \
              '{:<10}'.format('ROW')

        if format == "league":
            standings_sorted = play_season.sort_by_points_row(standings)
            play_season.print_standings_tuple(standings_sorted)

        elif format == "conference":
            atlantic, metro, central, pacific = play_season.sort_standings_by_division_NHL(standings)
            east = play_season.merge_dicts(atlantic, metro)
            west = play_season.merge_dicts(central, pacific)
            print("\nEAST\n")
            play_season.print_standings_tuple(play_season.sort_by_points_row(east))
            print("\nWEST\n")
            play_season.print_standings_tuple(play_season.sort_by_points_row(west))

        elif format == "division":
            atlantic, metro, central, pacific = self.sort_standings_by_division_NHL(standings)
            print("\nATLANTIC\n")
            play_season.print_standings_tuple(play_season.sort_by_points_row(atlantic))
            print("\nMETROPOLITAN\n")
            play_season.print_standings_tuple(play_season.sort_by_points_row(metro))
            print("\nCENTRAL\n")
            play_season.print_standings_tuple(play_season.sort_by_points_row(central))
            print("\nPACIFIC\n")
            play_season.print_standings_tuple(play_season.sort_by_points_row(pacific))

        elif format == "wildcard":

            # These are also hard-coded elsew here... so maybe they shouldn't be!
            div_cutoff=3
            wc_cutoff=2

            atlantic, metro, central, pacific = play_season.sort_standings_by_division_NHL(standings)
            east = play_season.merge_dicts(atlantic, metro)
            west = play_season.merge_dicts(central, pacific)

            atlantic_sorted = play_season.sort_by_points_row(atlantic)
            metro_sorted = play_season.sort_by_points_row(metro)
            central_sorted = play_season.sort_by_points_row(central)
            pacific_sorted = play_season.sort_by_points_row(pacific)

            atlantic_top = dict()
            metro_top = dict()
            central_top = dict()
            pacific_top = dict()
            for i in xrange(div_cutoff):
                atlantic_top[atlantic_sorted[i][0]] = atlantic_sorted[i][1]
                metro_top[metro_sorted[i][0]] = metro_sorted[i][1]
                east.pop(atlantic_sorted[i][0])
                east.pop(metro_sorted[i][0])
                central_top[central_sorted[i][0]] = central_sorted[i][1]
                pacific_top[pacific_sorted[i][0]] = pacific_sorted[i][1]
                west.pop(central_sorted[i][0])
                west.pop(pacific_sorted[i][0])

            east_sorted = play_season.sort_by_points_row(east)
            west_sorted = play_season.sort_by_points_row(west)

            east_wc = dict()
            west_wc = dict()
            for i in xrange(wc_cutoff):
                east_wc[east_sorted[i][0]] = east_sorted[i][1]
                east.pop(east_sorted[i][0])
                west_wc[west_sorted[i][0]] = west_sorted[i][1]
                west.pop(west_sorted[i][0])

            print("\nEAST\n")
            print("ATLANTIC")
            print("------------------------------------------------------------------------")
            play_season.print_standings_tuple(play_season.sort_by_points_row(atlantic_top))
            print("------------------------------------------------------------------------")
            print("METROPOLITAN")
            print("------------------------------------------------------------------------")
            play_season.print_standings_tuple(play_season.sort_by_points_row(metro_top))
            print("------------------------------------------------------------------------")
            print("WILDCARD")
            print("------------------------------------------------------------------------")
            play_season.print_standings_tuple(play_season.sort_by_points_row(east_wc))
            print("------------------------------------------------------------------------")
            play_season.print_standings_tuple(play_season.sort_by_points_row(east))

            print("\nWEST\n")
            print("CENTRAL")
            print("------------------------------------------------------------------------")
            play_season.print_standings_tuple(play_season.sort_by_points_row(central_top))
            print("------------------------------------------------------------------------")
            print("PACIFIC")
            print("------------------------------------------------------------------------")
            play_season.print_standings_tuple(play_season.sort_by_points_row(pacific_top))
            print("------------------------------------------------------------------------")
            print("WILDCARD")
            print("------------------------------------------------------------------------")
            play_season.print_standings_tuple(play_season.sort_by_points_row(west_wc))
            print("------------------------------------------------------------------------")
            play_season.print_standings_tuple(play_season.sort_by_points_row(west))


        print("\n")

    @staticmethod
    def print_standings_tuple(standings_tup):
        for team in xrange(len(standings_tup)):
            print '{:<25}'.format(standings_tup[team][0]), \
                  '{:<10}'.format(standings_tup[team][1]["wins"]), \
                  '{:<10}'.format(standings_tup[team][1]["losses"]), \
                  '{:<10}'.format(standings_tup[team][1]["OTlosses"]), \
                  '{:<10}'.format(standings_tup[team][1]["points"]), \
                  '{:<10}'.format(standings_tup[team][1]["ROW"])

    @staticmethod
    # Create a dictionary to hold wins, losses, OT losses for each team
    def generate_initial_standings_NHL(teams):
        standings = {}
        for team in teams:
            standings[team.name] = {"wins": 0, "losses": 0, "OTlosses": 0, "points": 0, "ROW": 0,
                                                 "div": team.division }
        return standings

    @staticmethod
    def generate_standings_from_game_record(teams, game_record):
        standings = play_season.generate_initial_standings_NHL(teams)
        for game in game_record:
            if not game_record[game]["winner"]:
                continue
            winner = game_record[game]["winner"]
            if game_record[game]["visitor"] == winner:
                loser = game_record[game]["home"]
            else:
                loser = game_record[game]["visitor"]
            standings[winner]["wins"] += 1
            standings[winner]["points"] += 2
            # This bit isn't great, hard coding and probably not optimal
            OT = game_record[game]["OT"]
            if not OT:
                standings[winner]["ROW"] += 1
                standings[loser]["losses"] += 1
            elif OT == "OT":
                standings[winner]["ROW"] += 1
                standings[loser]["points"] += 1
                standings[loser]["OTlosses"] += 1
            elif OT == "SO":
                standings[loser]["points"] += 1
                standings[loser]["OTlosses"] += 1
        return standings

    @staticmethod
    # Utility function to sort by points and ROW, since we do this a lot
    def sort_by_points_row(standings):
        return sorted(standings.items(), key=lambda kv: (kv[1]['points'], kv[1]['ROW']), reverse=True)

    @staticmethod
    # Utility function to merge dictionaries (lol python 2)
    def merge_dicts(x, y):
        z = x.copy()
        z.update(y)
        return z

    @staticmethod
    # Utility function to swap elements in a tuple, used for tie breaking
    def swap_tuple_elements(tup, i, j):
        tmp = list(tup)
        tmp[i], tmp[j] = tmp[j], tmp[i]
        return tuple(tmp)

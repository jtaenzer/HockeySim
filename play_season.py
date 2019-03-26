import random
import copy


class PlaySeason:

    def __init__(self, teams, schedule, start):
        self.teams = teams
        self.schedule = schedule
        self.game_record = copy.deepcopy(self.schedule)
        self.standings = self.generate_initial_standings_nhl(self.teams)
        self.start = start

    # Run through the schedule and decide each game with a coin flip
    # Ideas/thoughts:
    # -Use a weighted coin flip instead, take weights for each team as an input
    # -Modify the initial weight based on each teams record
    #  Doing this in a simple way will be susceptible to fluctuations, how to avoid that? Cap the weight at some value?
    # -There should be a better way to do the entries to the standings dictionary...
    def play_games_simple(self, allow_ot=True):
        for i in xrange(len(self.game_record)):
            if i < self.start:
                continue
            sched_key = "game"+str(i)
            game = [self.schedule[sched_key]["visitor"], self.schedule[sched_key]["home"]]
            winner = random.choice(game)
            ot = self.overtime_check() if allow_ot else ""
            self.game_record[sched_key].update({"winner": winner})
            self.game_record[sched_key].update({'OT': ot})

        self.standings = self.generate_standings_from_game_record(self.teams, self.game_record)

    # Determine which teams made the playoffs based on the NHL wildcard format
    # Tie-breaking based on ROW is implemented
    # Tie-breaking based on head-to-head games and goals scored not implemented. Not clear how to do this yet.
    def determine_playoffs_nhl(self, result):

        # Should these by hard coded??
        div_cutoff = 3  # top 3 teams from each division automatically make the playoffs
        wildcard_cutoff = 2  # The top 2 teams from each conference that didn't get a div spot take the wildcard spots

        atlantic, metro, central, pacific = self.sort_standings_by_division_nhl(self.standings)
        east = self.merge_dicts(atlantic, metro)
        west = self.merge_dicts(central, pacific)

        atlantic_sorted = self.chk_tiebreaks_nhl(self.sort_by_points_row(atlantic))
        metro_sorted = self.chk_tiebreaks_nhl(self.sort_by_points_row(metro))
        central_sorted = self.chk_tiebreaks_nhl(self.sort_by_points_row(central))
        pacific_sorted = self.chk_tiebreaks_nhl(self.sort_by_points_row(pacific))

        for i in xrange(div_cutoff):
            result[atlantic_sorted[i][0]] += 1
            result[metro_sorted[i][0]] += 1
            east.pop(atlantic_sorted[i][0])
            east.pop(metro_sorted[i][0])
            result[central_sorted[i][0]] += 1
            result[pacific_sorted[i][0]] += 1
            west.pop(central_sorted[i][0])
            west.pop(pacific_sorted[i][0])

        east_sorted = self.chk_tiebreaks_nhl(self.sort_by_points_row(east))
        west_sorted = self.chk_tiebreaks_nhl(self.sort_by_points_row(west))

        for i in xrange(wildcard_cutoff):
            result[east_sorted[i][0]] += 1
            result[west_sorted[i][0]] += 1

    # This method checks for ties and re-orders the standings based on tie-breakers
    # For now only the head-to-head record is checked
    def chk_tiebreaks_nhl(self, standings_sorted):
        checkedpairs = []
        for i in xrange(len(standings_sorted)):
            for j in xrange(len(standings_sorted)):
                if i == j:
                    continue
                if [i, j] in checkedpairs or [j, i] in checkedpairs:
                    continue
                points_i = standings_sorted[i][1]["points"]
                points_j = standings_sorted[j][1]["points"]
                row_i = standings_sorted[i][1]["ROW"]
                row_j = standings_sorted[j][1]["ROW"]
                if points_i == points_j and row_i == row_j:
                    team_i = standings_sorted[i][0]
                    team_j = standings_sorted[j][0]
                    if self.chk_head_to_head_nhl(team_i, team_j) == team_j:
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
    def chk_head_to_head_nhl(self, team1, team2):

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
            for i in xrange(len(head_to_head_sorted)):
                count[head_to_head_sorted[i][1]["home"]] += 1
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
    # Used in determine_playoffs_simple_nhl()
    @staticmethod
    def sort_standings_by_division_nhl(standings):
        atlantic = dict()
        metro = dict()
        central = dict()
        pacific = dict()

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
    def print_standings_sorted(standings, output_format="league"):

        print '{:<25}'.format('Team'), \
              '{:<10}'.format('Wins'), \
              '{:<10}'.format('Losses'), \
              '{:<10}'.format('OT Losses'), \
              '{:<10}'.format('Points'), \
              '{:<10}'.format('ROW')

        if output_format == "league":
            standings_sorted = PlaySeason.sort_by_points_row(standings)
            PlaySeason.print_standings_tuple(standings_sorted)

        elif output_format == "conference":
            atlantic, metro, central, pacific = PlaySeason.sort_standings_by_division_nhl(standings)
            east = PlaySeason.merge_dicts(atlantic, metro)
            west = PlaySeason.merge_dicts(central, pacific)
            print("\nEAST\n")
            PlaySeason.print_standings_tuple(PlaySeason.sort_by_points_row(east))
            print("\nWEST\n")
            PlaySeason.print_standings_tuple(PlaySeason.sort_by_points_row(west))

        elif output_format == "division":
            atlantic, metro, central, pacific = PlaySeason.sort_standings_by_division_nhl(standings)
            print("\nATLANTIC\n")
            PlaySeason.print_standings_tuple(PlaySeason.sort_by_points_row(atlantic))
            print("\nMETROPOLITAN\n")
            PlaySeason.print_standings_tuple(PlaySeason.sort_by_points_row(metro))
            print("\nCENTRAL\n")
            PlaySeason.print_standings_tuple(PlaySeason.sort_by_points_row(central))
            print("\nPACIFIC\n")
            PlaySeason.print_standings_tuple(PlaySeason.sort_by_points_row(pacific))

        elif output_format == "wildcard":

            # These are also hard-coded elsew here... so maybe they shouldn't be!
            div_cutoff = 3
            wc_cutoff = 2

            atlantic, metro, central, pacific = PlaySeason.sort_standings_by_division_nhl(standings)
            east = PlaySeason.merge_dicts(atlantic, metro)
            west = PlaySeason.merge_dicts(central, pacific)

            atlantic_sorted = PlaySeason.sort_by_points_row(atlantic)
            metro_sorted = PlaySeason.sort_by_points_row(metro)
            central_sorted = PlaySeason.sort_by_points_row(central)
            pacific_sorted = PlaySeason.sort_by_points_row(pacific)

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

            east_sorted = PlaySeason.sort_by_points_row(east)
            west_sorted = PlaySeason.sort_by_points_row(west)

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
            PlaySeason.print_standings_tuple(PlaySeason.sort_by_points_row(atlantic_top))
            print("------------------------------------------------------------------------")
            print("METROPOLITAN")
            print("------------------------------------------------------------------------")
            PlaySeason.print_standings_tuple(PlaySeason.sort_by_points_row(metro_top))
            print("------------------------------------------------------------------------")
            print("WILDCARD")
            print("------------------------------------------------------------------------")
            PlaySeason.print_standings_tuple(PlaySeason.sort_by_points_row(east_wc))
            print("------------------------------------------------------------------------")
            PlaySeason.print_standings_tuple(PlaySeason.sort_by_points_row(east))

            print("\nWEST\n")
            print("CENTRAL")
            print("------------------------------------------------------------------------")
            PlaySeason.print_standings_tuple(PlaySeason.sort_by_points_row(central_top))
            print("------------------------------------------------------------------------")
            print("PACIFIC")
            print("------------------------------------------------------------------------")
            PlaySeason.print_standings_tuple(PlaySeason.sort_by_points_row(pacific_top))
            print("------------------------------------------------------------------------")
            print("WILDCARD")
            print("------------------------------------------------------------------------")
            PlaySeason.print_standings_tuple(PlaySeason.sort_by_points_row(west_wc))
            print("------------------------------------------------------------------------")
            PlaySeason.print_standings_tuple(PlaySeason.sort_by_points_row(west))
        print("\n")

    # Decide if a game went to overtime assuming 25% of games go to OT
    @staticmethod
    def overtime_check():
        result = random.randint(0, 100)
        # Approximate numbers stolen from an article about 3on3 OT
        # Regulation - 75%, OT - 15%, SO - 10%
        if result >= 90:
            return "SO"
        elif 75 <= result < 90:
            return "OT"
        else:
            return ""

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
    def generate_initial_standings_nhl(teams):
        standings = {}
        for team in teams:
            standings[team.name] = {"wins": 0, "losses": 0, "OTlosses": 0, "points": 0, "ROW": 0, "div": team.division}
        return standings

    @staticmethod
    def generate_standings_from_game_record(teams, game_record, end=None):
        standings = PlaySeason.generate_initial_standings_nhl(teams)

        for i in xrange(len(game_record)):
            game_key = "game"+str(i)
            if end is not None and i >= end:
                continue
            elif not game_record[game_key]["winner"]:
                continue
            winner = game_record[game_key]["winner"]
            if game_record[game_key]["visitor"] == winner:
                loser = game_record[game_key]["home"]
            else:
                loser = game_record[game_key]["visitor"]
            standings[winner]["wins"] += 1
            standings[winner]["points"] += 2
            # This bit isn't great, hard coding and probably not optimal
            ot = game_record[game_key]["OT"]
            if not ot:
                standings[winner]["ROW"] += 1
                standings[loser]["losses"] += 1
            elif ot == "OT":
                standings[winner]["ROW"] += 1
                standings[loser]["points"] += 1
                standings[loser]["OTlosses"] += 1
            elif ot == "SO":
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

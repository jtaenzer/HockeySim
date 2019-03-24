import random, copy

class play_season:

    def __init__(self, teams_file_path, schedule):
        self.teams_file_path = teams_file_path
        self.schedule        = schedule
        self.game_record     = copy.deepcopy(self.schedule)
        self.standings       = self.generate_initial_standings_NHL()

    # Create a dictionary to hold wins, losses, OT losses for each team
    def generate_initial_standings_NHL(self):
        standings = {}
        teams_file = open(self.teams_file_path, 'r')
        for line in teams_file:
            line_mod = line.replace('\n', '')
            standings[line_mod.split(',')[0]] = {"wins": 0, "losses": 0, "OTlosses": 0, "points": 0, "ROW": 0,
                                                 "div": line_mod.split(',')[1]}
        return standings

    # Run through the schedule and decide each game with a coin flip
    # Ideas/thoughts:
    # -Use a weighted coin flip instead, take weights for each team as an input
    # -Modify the initial weight based on each teams record
    #  Doing this in a simple way will be susceptible to fluctuations, how to avoid that? Cap the weight at some value?
    # -There should be a better way to do the entries to the standings dictionary...
    def play_games_simple(self, allowOT=True):

        for day in self.game_record:
            game = [self.schedule[day]["visitor"], self.schedule[day]["home"]]
            winner = random.choice(game)
            self.game_record[day].update({"winner": winner})
            if allowOT:
                OT = self.overtime_check()
            else:
                OT = "REG"
            self.game_record[day].update({'OT': OT})

        self.generate_standings_from_game_record()

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
            return "REG"

    def generate_standings_from_game_record(self):
        for game in self.game_record:
            winner = self.game_record[game]["winner"]
            if self.game_record[game]["visitor"] == winner:
                loser = self.game_record[game]["home"]
            else:
                loser = self.game_record[game]["visitor"]
            self.standings[winner]["wins"] += 1
            self.standings[winner]["points"] += 2
            # This bit isn't great, hard coding and probably not optimal
            OT = self.game_record[game]["OT"]
            if OT == "REG":
                self.standings[winner]["ROW"] += 1
                self.standings[loser]["losses"] += 1
            elif OT == "OT":
                self.standings[winner]["ROW"] += 1
                self.standings[loser]["points"] += 1
                self.standings[loser]["OTlosses"] += 1
            elif OT == "SO":
                self.standings[loser]["points"] += 1
                self.standings[loser]["OTlosses"] += 1

    # Determine which teams made the playoffs based on the NHL wildcard format
    # Tie-breaking based on ROW is implemented
    # Tie-breaking based on head-to-head games and goals scored not implemented. Not clear how to do this yet.
    def determine_playoffs_NHL(self,result):

        # Should these by hard coded??
        Nteams = 16  # number of teams that can make the playoffs
        div_cutoff = 3  # top 3 teams from each division automatically make the playoffs
        wildcard_cutoff = 2  # The top 2 teams from each conference that didn't get a div spot take the wildcard spots

        atlantic, metro, central, pacific = self.sort_standings_by_division_NHL()
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
            east.pop(atlantic_sorted[i][0]);
            east.pop(metro_sorted[i][0])
            result[central_sorted[i][0]] += 1
            result[pacific_sorted[i][0]] += 1
            west.pop(central_sorted[i][0]);
            west.pop(pacific_sorted[i][0]);

        east_sorted = self.chk_tiebreaks_NHL(self.sort_by_points_row(east))
        west_sorted = self.chk_tiebreaks_NHL(self.sort_by_points_row(west))

        for i in xrange(wildcard_cutoff):
            result[east_sorted[i][0]] += 1
            result[west_sorted[i][0]] += 1

    # Sort the standings by NHL divisions
    # Used in determine_playoffs_simple_NHL()
    def sort_standings_by_division_NHL(self):
        atlantic = dict()
        metro    = dict()
        central  = dict()
        pacific  = dict()

        for team in self.standings:
            if self.standings[team]['div'] == 'a':
                atlantic[team] = self.standings[team]
            elif self.standings[team]['div'] == 'm':
                metro[team] = self.standings[team]
            elif self.standings[team]['div'] == 'c':
                central[team] = self.standings[team]
            elif self.standings[team]['div'] == 'p':
                pacific[team] = self.standings[team]

        return atlantic, metro, central, pacific

    # This method checks for ties and re-orders the standings based on tie-breakers
    # For now only the head-to-head record is checked
    def chk_tiebreaks_NHL(self, standings_sorted):
        checkedpairs = []
        for i in xrange(len(standings_sorted)):
            for j in xrange(len(standings_sorted)):
                if i == j: continue
                if [i, j] in checkedpairs or [j, i] in checkedpairs: continue
                if standings_sorted[i][1]["points"] == standings_sorted[j][1]["points"] and standings_sorted[i][1][
                   "ROW"] == standings_sorted[j][1]["ROW"]:
                    if self.chk_head_to_head_NHL(standings_sorted[i][0], standings_sorted[j][0]) == standings_sorted[j][0]:
                        standings_sorted = self.swap_tuple_elements(standings_sorted, i, j)
                checkedpairs.append([i, j])
        return standings_sorted

    # Check the head to head record for tie breaking
    # Rules (per NHL.com):
    # Team with that earned the most points in games between the two teams wins the tie-break
    # When the teams played an odd number of games, points earned in the first game played in the city that had the extra game shall not be included.
    # The last fallback if the teams are still tied is the team with the greater goal differential -- not clear what to do there, just return random for now
    def chk_head_to_head_NHL(self, team1, team2):

        # First for convenience find the head-to-head games in our self.game_record and put them in a smaller dictionary
        head_to_head = dict()
        for game in self.game_record:
            if (self.game_record[game]["home"] == team1 or self.game_record[game]["visitor"] == team1) and (
                    self.game_record[game]["home"] == team2 or self.game_record[game]["visitor"] == team2):
                head_to_head[game] = (self.game_record[game])

        # For odd numbers of games, determine which team had more home games and "pop" their first home game from head_to_head
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
                if count[head_to_head_sorted[i][1]["home"]] == pop_team: head_to_head.pop(head_to_head_sorted[i][0])

        # Determine how many points each team earned in their games against each other
        team1_pts = 0
        team2_pts = 0
        for game in head_to_head:
            if self.game_record[game]["winner"] == team1:
                team1_pts += 2
                if self.game_record[game]["OT"] == "OT" or self.game_record[game]["OT"] == "SO": team2_pts += 1
            elif self.game_record[game]["winner"] == team2:
                team2_pts += 2
                if self.game_record[game]["OT"] == "OT" or self.game_record[game]["OT"] == "SO": team1_pts += 1

        if team1_pts > team2_pts:
            return team1
        elif team2_pts < team1_pts:
            return team2
        else:
            return random.choice([team1, team2])  # If they're still tied, just return a random choice

    # Print sorted standings, for debugging
    # This doesn't get called anywhere at the moment
    def print_standings_sorted(self):
        standings_sorted = self.chk_tiebreaks_NHL(sort_by_points_row(self.standings))
        print('{:<25}'.format('Team'),
              '{:<10}'.format('Wins'),
              '{:<10}'.format('Losses'),
              '{:<10}'.format('OT Losses'),
              '{:<10}'.format('Points'),
              '{:<10}'.format('ROW'))

        for team in xrange(len(standings_sorted)):
            print('{:<25}'.format(standings_sorted[team][0]),
                  '{:<10}'.format(standings_sorted[team][1]["wins"]),
                  '{:<10}'.format(standings_sorted[team][1]["losses"]),
                  '{:<10}'.format(standings_sorted[team][1]["OTlosses"]),
                  '{:<10}'.format(standings_sorted[team][1]["points"]),
                  '{:<10}'.format(standings_sorted[team][1]["ROW"]))

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
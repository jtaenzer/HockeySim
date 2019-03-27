from __future__ import division
from play_season import PlaySeason
import random


class PlaySeasonNHL(PlaySeason):

    def __init__(self, teams, schedule, start):
        PlaySeason.__init__(self, teams, schedule, start)
        self.standings = self.generate_initial_standings(self.teams)
        self.div_cutoff = 3  # Number of teams from each division that make the playoffs
        self.wc_cutoff = 2  # Number of teams from each conference that make the playoffs as wildcards

    # This doesn't really return a weight...
    # Calculates the point % of both teams, normalizes the sum to 1 and returns the mid point
    # The end result is that the team with the greater point % will be more likely to win
    def get_weight(self, game):
        # Sanity check, game should always be a list of two teams
        if len(game) != 2:
            print("PlaySeasonNHL.get_weight : len(game) != 2, returning coin flip")
            return 50

        point_percent = []
        sum = 0
        for team in game:
            points = self.standings[team]["points"]
            games_played = self.standings[team]["wins"] + self.standings[team]["losses"] + \
                           self.standings[team]["OTlosses"]
            # Return a coin flip if one of the teams hasn't no points or games played
            if points == 0 or games_played == 0:
                return 50
            point_percent.append(points/games_played)
            sum+=point_percent[-1]

        weight = 1 - point_percent[0] / sum
        if weight < 0 or weight > 1:
            print("PlaySeasonNHL.get_weight : weight (%s) is less than 0 or greater than 1, returning coin flip"
                  % str(weight))
            return 50

        return 100*weight

    def update_standings(self, game, winner, ot=""):
        # loop over teams in game and update standings accordingly
        for team in game:
            if team == winner:
                self.standings[team]["wins"] += 1
                ROW = 1 if ot != "SO" else 0 # SO wins don't get added to ROW
                self.standings[team]["ROW"] += ROW
                self.standings[team]["points"] += 2
            else:
                if ot: # ot is an empty string for games decided in regulation
                    self.standings[team]["OTlosses"] += 1
                    self.standings[team]["points"] += 1
                else:
                    self.standings[team]["losses"] += 1

    # Fill the result dictionary with whatever information we want to save
    # The format of result is determine elsewhere, could cause trouble later
    def update_result(self, result):
        playoff_teams = self.determine_playoffs()
        for team in self.teams:
            if team.name in playoff_teams:
                result[team.name]["playoffs"] += 1
            result[team.name]["wins"] += self.standings[team.name]["wins"]
            result[team.name]["losses"] += self.standings[team.name]["losses"]
            result[team.name]["ROW"] += self.standings[team.name]["ROW"]
            result[team.name]["OTlosses"] += self.standings[team.name]["OTlosses"]
            result[team.name]["points"] += self.standings[team.name]["points"]


    # Determine which teams made the playoffs based on the NHL wildcard format
    # Tie-breaking based on ROW and head to head records are implemented
    # Tie-breaking based on goal differential is not implemented, requires more thought
    # This method could be static if we passed the standings to it, should it be?
    def determine_playoffs(self):
        playoff_team_list = []
        atlantic, metro, central, pacific = self.sort_standings_by_division(self.teams, self.standings)
        east = self.merge_dicts(atlantic, metro)
        west = self.merge_dicts(central, pacific)

        atlantic_sorted = self.chk_tiebreaks(self.sort_by_points_row(atlantic))
        metro_sorted = self.chk_tiebreaks(self.sort_by_points_row(metro))
        central_sorted = self.chk_tiebreaks(self.sort_by_points_row(central))
        pacific_sorted = self.chk_tiebreaks(self.sort_by_points_row(pacific))

        # Find the top self.div_cutoff (3) teams in each division and add them to playoff_team_list
        # Pop those same teams from east and west so we can use east and west to determine the wildcard spots
        for i in xrange(self.div_cutoff):
            playoff_team_list.append(atlantic_sorted[i][0])
            playoff_team_list.append(metro_sorted[i][0])
            playoff_team_list.append(central_sorted[i][0])
            playoff_team_list.append(pacific_sorted[i][0])
            east.pop(atlantic_sorted[i][0])
            east.pop(metro_sorted[i][0])
            west.pop(central_sorted[i][0])
            west.pop(pacific_sorted[i][0])

        east_sorted = self.chk_tiebreaks(self.sort_by_points_row(east))
        west_sorted = self.chk_tiebreaks(self.sort_by_points_row(west))

        for i in xrange(self.wc_cutoff):
            playoff_team_list.append(east_sorted[i][0])
            playoff_team_list.append(west_sorted[i][0])

        return playoff_team_list

    # This method checks for ties and re-orders the standings based on tie-breakers
    # For now only the head-to-head record is checked
    def chk_tiebreaks(self, standings_sorted):
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
                    if self.chk_head_to_head(team_i, team_j) == team_j:
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
    def chk_head_to_head(self, team1, team2):

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

    # Decide if a game went to overtime assuming 25% of games go to OT and 10% go to SO
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

    # Sort the standings by NHL divisions
    # Used in determine_playoffs_simple()
    @staticmethod
    def sort_standings_by_division(teams, standings):
        atlantic = dict()
        metro = dict()
        central = dict()
        pacific = dict()

        for team in teams:
            if team.division == 'a':
                atlantic[team.name] = standings[team.name]
            elif team.division == 'm':
                metro[team.name] = standings[team.name]
            elif team.division == 'c':
                central[team.name] = standings[team.name]
            elif team.division == 'p':
                pacific[team.name] = standings[team.name]

        return atlantic, metro, central, pacific

    # Prints the standings in a nicely formatted way
    # Currently gets called to print initial standings when starting a sim mid-season
    @staticmethod
    def print_standings_sorted(teams, standings, output_format="wildcard"):

        print '{:<25}'.format('Team'), \
              '{:<10}'.format('Wins'), \
              '{:<10}'.format('Losses'), \
              '{:<10}'.format('OT Losses'), \
              '{:<10}'.format('Points'), \
              '{:<10}'.format('ROW')

        if output_format == "league":
            standings_sorted = PlaySeasonNHL.sort_by_points_row(standings)
            PlaySeasonNHL.print_standings_tuple(standings_sorted)

        elif output_format == "conference":
            atlantic, metro, central, pacific = PlaySeasonNHL.sort_standings_by_division(teams, standings)
            east = PlaySeasonNHL.merge_dicts(atlantic, metro)
            west = PlaySeasonNHL.merge_dicts(central, pacific)
            print("\nEAST\n")
            PlaySeasonNHL.print_standings_tuple(PlaySeasonNHL.sort_by_points_row(east))
            print("\nWEST\n")
            PlaySeasonNHL.print_standings_tuple(PlaySeasonNHL.sort_by_points_row(west))

        elif output_format == "division":
            atlantic, metro, central, pacific = PlaySeasonNHL.sort_standings_by_division(teams, standings)
            print("\nATLANTIC\n")
            PlaySeasonNHL.print_standings_tuple(PlaySeasonNHL.sort_by_points_row(atlantic))
            print("\nMETROPOLITAN\n")
            PlaySeasonNHL.print_standings_tuple(PlaySeasonNHL.sort_by_points_row(metro))
            print("\nCENTRAL\n")
            PlaySeasonNHL.print_standings_tuple(PlaySeasonNHL.sort_by_points_row(central))
            print("\nPACIFIC\n")
            PlaySeasonNHL.print_standings_tuple(PlaySeasonNHL.sort_by_points_row(pacific))

        elif output_format == "wildcard":

            # These are also hard-coded elsew here... so maybe they shouldn't be!
            div_cutoff = 3
            wc_cutoff = 2

            atlantic, metro, central, pacific = PlaySeasonNHL.sort_standings_by_division(teams, standings)
            east = PlaySeasonNHL.merge_dicts(atlantic, metro)
            west = PlaySeasonNHL.merge_dicts(central, pacific)

            atlantic_sorted = PlaySeasonNHL.sort_by_points_row(atlantic)
            metro_sorted = PlaySeasonNHL.sort_by_points_row(metro)
            central_sorted = PlaySeasonNHL.sort_by_points_row(central)
            pacific_sorted = PlaySeasonNHL.sort_by_points_row(pacific)

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

            east_sorted = PlaySeasonNHL.sort_by_points_row(east)
            west_sorted = PlaySeasonNHL.sort_by_points_row(west)

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
            PlaySeasonNHL.print_standings_tuple(PlaySeasonNHL.sort_by_points_row(atlantic_top))
            print("------------------------------------------------------------------------")
            print("METROPOLITAN")
            print("------------------------------------------------------------------------")
            PlaySeasonNHL.print_standings_tuple(PlaySeasonNHL.sort_by_points_row(metro_top))
            print("------------------------------------------------------------------------")
            print("WILDCARD")
            print("------------------------------------------------------------------------")
            PlaySeasonNHL.print_standings_tuple(PlaySeasonNHL.sort_by_points_row(east_wc))
            print("------------------------------------------------------------------------")
            PlaySeasonNHL.print_standings_tuple(PlaySeasonNHL.sort_by_points_row(east))

            print("\nWEST\n")
            print("CENTRAL")
            print("------------------------------------------------------------------------")
            PlaySeasonNHL.print_standings_tuple(PlaySeasonNHL.sort_by_points_row(central_top))
            print("------------------------------------------------------------------------")
            print("PACIFIC")
            print("------------------------------------------------------------------------")
            PlaySeasonNHL.print_standings_tuple(PlaySeasonNHL.sort_by_points_row(pacific_top))
            print("------------------------------------------------------------------------")
            print("WILDCARD")
            print("------------------------------------------------------------------------")
            PlaySeasonNHL.print_standings_tuple(PlaySeasonNHL.sort_by_points_row(west_wc))
            print("------------------------------------------------------------------------")
            PlaySeasonNHL.print_standings_tuple(PlaySeasonNHL.sort_by_points_row(west))
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
    def generate_initial_standings(teams):
        standings = {}
        for team in teams:
            standings[team.name] = {"wins": 0, "losses": 0, "OTlosses": 0, "points": 0, "ROW": 0, "div": team.division}
        return standings

    @staticmethod
    def generate_standings_from_game_record(teams, game_record, end=None):
        standings = PlaySeasonNHL.generate_initial_standings(teams)

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

    # Create an empty dictionary to hold the simulated result
    # For now the result is just the count of how many times each team makes the playoffs
    # More information that could be be added:
    # - avg wins/losses/pts
    # -
    # This method is in PlaySeason (and daughters) since the format of the result will depend on the league
    @staticmethod
    def prep_sim_result(teams):
        result = dict()
        for team in teams:
            result[team.name] = dict()
            result[team.name].update({"playoffs": 0})
            result[team.name].update({"wins": 0})
            result[team.name].update({"losses": 0})
            result[team.name].update({"OTlosses": 0})
            result[team.name].update({"points": 0})
            result[team.name].update({"ROW": 0})
        return result
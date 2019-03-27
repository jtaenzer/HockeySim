from __future__ import division
import time
import sys
import datetime

from schedule_maker import ScheduleMaker
from play_season_nhl import PlaySeasonNHL
from team_info import TeamInfo


class Simulation:

    def __init__(self, iterations, league, teams_file_path, schedule_file_path, season_start="auto"):

        # Number of times to play the season
        self.iterations = iterations

        # Set up the list of team_info class objects based on the text file provided
        # No protection against bad input yet...
        self.teams_path = teams_file_path
        self.teams = self.read_teams_file(teams_file_path)

        # Set result to None initially, if it is still None later the sim won't run
        self.result = None

        # For now the only supported league is "NHL" and it is only used to set Ngames
        # Could be used for more in the future
        self.league = league
        if self.league == "NHL":
            self.season_obj = PlaySeasonNHL
            self.Ngames = 82
            self.result = self.season_obj.prep_sim_result(self.teams)
        else:  # this if-else sequence basically does nothing for now
            print("%s is not supported as a league" % self.league)
            print("Using default settings with league=\"NHL\", this may break the schedule maker")
            self.season_obj = PlaySeasonNHL
            self.Ngames = 82
            self.result = self.season_obj.prep_sim_result(self.teams)

        # Set up the schedule based on the text file provided
        # No protection against bad input yet...
        self.schedule_path = schedule_file_path
        schedmaker = ScheduleMaker(self.league, self.teams, self.Ngames, self.schedule_path)
        self.schedule = schedmaker.schedule

        # Protection against bad season_start input
        # Really not sure this belongs in this class, but its convenient for now
        first_unplayed_game = schedmaker.find_first_unplayed_game(self.schedule)
        if season_start != "auto":
            # Check if season_start can be converted to a datetime
            try:
                self.season_start_date = datetime.datetime.strptime(season_start, '%Y-%m-%d')
                self.season_start = schedmaker.find_game_number_by_date(self.schedule, self.season_start_date)
            except (TypeError, ValueError) as e:
                # If it isn't a date, it might be an integer
                try:
                    self.season_start = int(season_start)
                    self.season_start_date = schedmaker.find_game_date_by_number(self.schedule, self.season_start)
                except ValueError:
                    print("Couldn't convert season_start (%s) to a YYYY-MM-DD date or to an integer, defaulting to "
                          "auto" % self.season_start)
                    self.season_start = "auto"

            if type(self.season_start) is int and first_unplayed_game < self.season_start:
                print("The first unplayed game is before season_start, defaulting back to auto")
                self.season_start = first_unplayed_game
                self.season_start_date = schedmaker.find_game_date_by_number(self.schedule, self.season_start)
        else:
            self.season_start = first_unplayed_game
            self.season_start_date = schedmaker.find_game_date_by_number(self.schedule, self.season_start)

    def run_simulation(self):
        if not self.schedule:
            print("Schedule dictionary is empty, can't sim.")
            return

        print("Generating initial standings from date %s\n" % self.season_start_date.date())
        # Here we use our season object to call some static methods from whichever class
        standings = self.season_obj.generate_standings_from_game_record(self.teams, self.schedule, self.season_start)
        self.season_obj.print_standings_sorted(self.teams, standings)

        print("Running simulation with %i iterations" % self.iterations)

        # set up progress bar
        toolbar_width = 100
        # Make sure the number of iterations is a multiple of 100
        if self.iterations % toolbar_width != 0:
            self.iterations -= self.iterations % toolbar_width
        sys.stdout.write("Progress: [%s]" % (" " * toolbar_width))
        sys.stdout.flush()
        sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['

        for i in xrange(self.iterations):

            season = None
            if self.league == "NHL":
                season = PlaySeasonNHL(self.teams, self.schedule, self.season_start)
            if season and self.result:  # We need both of these to exist or things will break later
                season.play_games_simple()
                season.update_result(self.result)
            else:
                print "Couldn't determine what kind of season to play, aborting."
                break

            # Update the progress bar
            if i % (self.iterations/toolbar_width) == 0:
                sys.stdout.write("-")
                sys.stdout.flush()

        print("\nDone, printing result")
        self.print_sim_result_sorted()

    # Reset the result
    def clear_sim_result(self):
        self.result = self.season_obj.prep_sim_result(self.teams)

    # Will replace print_sim_result
    # Should print every quantity in result in a nicely formatted way
    # Potentially needs to be moved into play_season_* if it is to be organized according to league structure
    def print_sim_result(self):
        # This shouldn't be hardcoded, figure out how to fix it later
        var_order = ["playoffs", "points", "ROW", "wins", "losses", "OTlosses"]

        head_str = '{:<25}'.format('Team')
        head_str += '{:<20}'.format('Avg Playoff %')
        head_str += '{:<15}'.format('Avg Points')
        head_str += '{:<15}'.format('Avg ROW')
        head_str += '{:<15}'.format('Avg Wins')
        head_str += '{:<15}'.format('Avg Losses')
        head_str += '{:<15}'.format('Avg OT Losses')
        print("")
        print head_str

        for team in self.result:
            team_str = '{:<25}'.format(team)
            for var_key in var_order:
                quantity = self.result[team][var_key] / self.iterations
                if var_key == "playoffs":
                    quantity = 100*quantity
                    team_str += '{:<20}'.format(str(quantity)+"%")
                else:
                    team_str += '{:<15}'.format(str(quantity))
            print team_str

    def print_sim_result_sorted(self):
        # This shouldn't be hardcoded, figure out how to fix it later
        var_order = ["playoffs", "points", "ROW", "wins", "losses", "OTlosses"]

        head_str = '{:<25}'.format('Team')
        head_str += '{:<20}'.format('Avg Playoff %')
        head_str += '{:<15}'.format('Avg Points')
        head_str += '{:<15}'.format('Avg ROW')
        head_str += '{:<15}'.format('Avg Wins')
        head_str += '{:<15}'.format('Avg Losses')
        head_str += '{:<15}'.format('Avg OT Losses')

        atlantic, metro, central, pacific = self.season_obj.sort_standings_by_division(self.teams, self.result)
        east = self.season_obj.merge_dicts(atlantic, metro)
        west = self.season_obj.merge_dicts(central, pacific)
        east_sorted = sorted(east.items(), key=lambda kv: kv[1]["playoffs"], reverse=True)
        west_sorted = sorted(west.items(), key=lambda kv: kv[1]["playoffs"], reverse=True)

        print("\nEAST\n")
        print(head_str)
        print("-------------------------------------------------------------------------------------------------------")
        for i in xrange(len(east_sorted)):
            team_str = '{:<25}'.format(east_sorted[i][0])
            for var_key in var_order:
                quantity = east_sorted[i][1][var_key]/self.iterations
                if var_key == "playoffs":
                    quantity = 100*quantity
                    team_str += '{:<20}'.format(str(quantity)+"%")
                else:
                    team_str += '{:<15}'.format(str(quantity))
            print team_str

        print("\nWEST\n")
        print(head_str)
        print("-------------------------------------------------------------------------------------------------------")
        for i in xrange(len(west_sorted)):
            team_str = '{:<25}'.format(west_sorted[i][0])
            for var_key in var_order:
                quantity = west_sorted[i][1][var_key] / self.iterations
                if var_key == "playoffs":
                    quantity = 100 * quantity
                    team_str += '{:<20}'.format(str(quantity) + "%")
                else:
                    team_str += '{:<15}'.format(str(quantity))
            print team_str

    @staticmethod
    def read_teams_file(path):
        teams = []
        teams_file = open(path, 'r')
        for line in teams_file:
            name = line.split(',')[0]
            div = line.split(',')[1].replace('\n', '')
            team = TeamInfo(name, div)
            teams.append(team)
        return teams

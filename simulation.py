from __future__ import division
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
        self.season_obj.print_standings_sorted(standings)

        print("Running simulation with %i iterations" % self.iterations)
        for i in xrange(self.iterations):
            if i % 100000 == 0:  # "poor man's progress bar"
                print "running sim", i
            season = None
            if self.league == "NHL":
                season = PlaySeasonNHL(self.teams, self.schedule, self.season_start)
            if season and self.result:  # We need both of these to exist or things will break later
                season.play_games_simple()
                season.update_result(self.result)
            else:
                print "Couldn't determine what kind of season to play, aborting."
                break

        print("Done, printing result")
        self.print_sim_result("Playoff %")

    # Print the result dictionary
    def print_sim_result(self, quantity, mult=100):
        print("")
        print("%s %s" % ('{:<25}'.format('Team'), quantity))
        for team in self.result:
            mult_quantity = mult * self.result[team]["playoffs"] / self.iterations
            print("%s %.2f" % ('{:<25}'.format(team), mult_quantity))
        print("")

    # Will replace print_sim_result
    # Should print every quantity in result in a nicely formatted way
    # Potentially needs to be moved into play_season_* if it is to be organized according to league structure
    def print_sim_result_new(self):
        print("under construction...")

    # Reset the result
    def clear_sim_result(self):
        self.result = self.season_obj.prep_sim_result(self.teams)

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

from __future__ import division
import datetime

from schedule_maker import schedule_maker
from play_season import play_season
from team_info import team_info


class simulation:

    def __init__(self, iterations, league, teams_file_path, schedule_file_path, season_start="auto"):

        # Number of times to play the season
        self.iterations = iterations

        # For now the only supported league is "NHL" and it is only used to set Ngames
        # Could be used for more in the future
        self.league = league
        if self.league == "NHL":
            self.Ngames = 82
        else:
            print("%s is not supported as a league" % self.league)
            print("Using default settings with league=\"NHL\", this may break the schedule maker")
            self.Ngames = 82

        # Set up the list of team_info class objects based on the text file provided
        # No protection against bad input yet...
        self.teams_path = teams_file_path
        self.teams = self.read_teams_file(teams_file_path)

        # Set up the schedule based on the text file provided
        # No protection against bad input yet...
        self.schedule_path = schedule_file_path
        schedmaker = schedule_maker(self.league, self.teams, self.Ngames, self.schedule_path)
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

        self.result = dict()

    # Create an empty dictionary to hold the simulated result
    # For now the result is just the count of how many times each team makes the playoffs
    # More information that could be be added:
    # - avg wins/losses/pts
    # -
    def prep_sim_result(self):
        for team in self.teams:
            self.result[team.name] = 0

    def run_simulation(self):
        if not self.schedule:
            print("Schedule dictionary is empty, can't sim.")
            return

        print("Generating initial standings from date %s\n" % self.season_start_date.date())
        standings = play_season.generate_standings_from_game_record(self.teams, self.schedule, self.season_start)
        play_season.print_standings_sorted(standings, "wildcard")

        self.prep_sim_result()
        print("Running simulation with %i iterations" % self.iterations)
        for i in xrange(self.iterations):
            if i % 1000 == 0:
                print "running sim", i
            season = play_season(self.teams, self.schedule, self.season_start)
            season.play_games_simple()
            season.determine_playoffs_nhl(self.result)

        print("Done, printing result")
        self.print_sim_result("Playoff %")

    # Print the result dictionary
    def print_sim_result(self, quantity, mult=100):
        print("")
        print("%s %s" % ('{:<25}'.format('Team'), quantity))
        for team in self.result:
            mult_quantity = mult * self.result[team] / self.iterations
            print("%s %.2f" % ('{:<25}'.format(team), mult_quantity))
        print("")

    @staticmethod
    def read_teams_file(path):
        teams = []
        teams_file = open(path, 'r')
        for line in teams_file:
            name = line.split(',')[0]
            div = line.split(',')[1].replace('\n', '')
            team = team_info(name, div)
            teams.append(team)
        return teams

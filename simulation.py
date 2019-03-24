from __future__ import division

from schedule_maker import schedule_maker
from play_season import play_season

class simulation:

    def __init__(self, iterations, league, teams_file_path, schedule_file_path):
        self.iterations    = iterations
        self.league        = league
        self.teams_path    = teams_file_path
        self.schedule_path = schedule_file_path

        if self.league == "NHL":
            self.Ngames = 82

        self.teams = []
        self.read_teams_file(teams_file_path)

        schedmaker = schedule_maker(self.league, self.teams, self.Ngames, self.schedule_path)
        self.schedule = schedmaker.schedule

        self.result = dict()

    def read_teams_file(self, path):
        teams_file = open(path, 'r')
        for line in teams_file:
            self.teams.append(line.split(',')[0])

    # Create an empty dictionary to hold the simulated result
    # For now the result is just the count of how many times each team makes the playoffs
    # More information that could be be added:
    # - avg wins/losses/pts
    # -
    def prep_sim_result(self):
        for team in self.teams:
            self.result[team] = 0

    def run_simulation(self):
        self.prep_sim_result()
        print("Running simulation with %i iterations" % self.iterations)
        for i in xrange(self.iterations):
            season = play_season(self.teams_path, self.schedule)
            season.play_games_simple()
            season.determine_playoffs_NHL(self.result)

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
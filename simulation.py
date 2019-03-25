from __future__ import division

from schedule_maker import schedule_maker
from play_season import play_season
from team_info import team_info


class simulation:

    def __init__(self, iterations, league, teams_file_path, schedule_file_path, season_start = "auto"):
        self.iterations    = iterations
        self.league        = league
        self.teams_path    = teams_file_path
        self.schedule_path = schedule_file_path
        self.season_start = season_start

        # Protection against bad season_start input
        if self.season_start != "auto":
            try:
                int(self.season_start)
            except:
                print("Couldn't convert season_start (%s) to an integer game value, defaulting to auto" %
                      self.season_start)
                self.season_start = "auto"

        if self.league == "NHL":
            self.Ngames = 82
        else:
            print("%s is not supported as a league" % self.league)
            print("Using default settings with league=\"NHL\", this may break the schedule maker")
            self.Ngames = 82

        self.teams = []
        self.read_teams_file(teams_file_path)

        schedmaker = schedule_maker(self.league, self.teams, self.Ngames, self.schedule_path)
        self.schedule = schedmaker.schedule

        self.result = dict()

    def read_teams_file(self, path):
        teams_file = open(path, 'r')
        for line in teams_file:
            name = line.split(',')[0]
            div = line.split(',')[1].replace('\n', '')
            team = team_info(name, div)
            self.teams.append(team)

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

        if self.season_start == "auto" or int(self.season_start) > 0:
            print("Generating initial standings...\n")
            standings = play_season.generate_standings_from_game_record(self.teams, self.schedule)
            play_season.print_standings_sorted(standings, "wildcard")

        self.prep_sim_result()
        print("Running simulation with %i iterations" % self.iterations)
        for i in xrange(self.iterations):
            season = play_season(self.teams, self.schedule, self.season_start)
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

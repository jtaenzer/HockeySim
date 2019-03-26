import random
import copy


class PlaySeason:

    def __init__(self, teams, schedule, start):
        self.teams = teams
        self.schedule = schedule
        self.game_record = copy.deepcopy(self.schedule)
        self.standings = None
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

    # This method should contain league specific rules so it isn't implemented here in the base class
    def update_result(self, result):
        print "determine_result should not be called from the base class.\n"

    # This method should contain league specific rules so it isn't implemented here in the base class
    def determine_playoffs(self):
        print "determine_playoffs should not be called from the base class.\n"

    # This method should contain league specific rules so it isn't implemented here in the base class
    def chk_tiebreaks(self, standings_sorted):
        print "chk_tiebreaks should not be called from the base class.\n"

    # This method should change depending on league specific rules so it isn't implemented here in the base class
    def chk_head_to_head(self, team1, team2):
        print "chk_head_to_head should not be called from the pass class.\n"

    # This method will always return an empty string (regulation win) and should be re-implemented in daughter classes
    @staticmethod
    def overtime_check():
        return ""

    # This method will depend on league specific information so it isn't implemented here in the base class
    @staticmethod
    def sort_standings_by_division(standings):
        print "sort_standings_by_division should not be called from the base class.\n"

    # This method will depend on league specific information so it isn't implemented here in the base class
    @staticmethod
    def print_standings_sorted(standings, output_format="league"):
        print "print_standings_sorted should not be called from the base class.\n"

    # Format of the standings may change from league to league so this is not implemented in the base class
    @staticmethod
    def print_standings_tuple(tup):
        print "print_standings_sorted should not be called from the base class.\n"

    # Format of the standings may change from league to league so this is not implemented in the base class
    @staticmethod
    def generate_initial_standings(teams):
        print "generate_initial_standings should not be called from the base class.\n"

    # Format of the standings may change from league to league so this is not implemented in the base class
    @staticmethod
    def generate_standings_from_game_record(teams, game_record, end=None):
        print "generate_standings_from_game_record should not be called from the base class.\n"

    # Format of the result may change from league to league so this is not implemented in the base class
    @staticmethod
    def prep_sim_result(teams):
        print "prep_sim_result should not be called from the base class.\n"

    # Utility function to sort standings by points
    # This will probably be replaced in the child classes to be better determine tiebreaks
    @staticmethod
    def sort_by_points(standings):
        return sorted(standings.items(), key=lambda kv: kv[1]['points'], reverse=True)

    # Utility function to merge dictionaries (lol python 2)
    @staticmethod
    def merge_dicts(x, y):
        z = x.copy()
        z.update(y)
        return z

    # Utility function to swap elements in a tuple, used for tie breaking
    @staticmethod
    def swap_tuple_elements(tup, i, j):
        tmp = list(tup)
        tmp[i], tmp[j] = tmp[j], tmp[i]
        return tuple(tmp)

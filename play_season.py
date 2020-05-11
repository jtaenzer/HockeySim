import random


class PlaySeason:

    def __init__(self, teams, game_record, start):
        self.teams = teams
        self.game_record = game_record
        self.standings = None # Has to be created in daughter classes
        self.start = start

    # Run through the schedule and decide each game with a coin flip
    # Ideas/thoughts:
    # -Use a weighted coin flip instead, take weights for each team as an input
    # -Modify the initial weight based on each teams record
    #  Doing this in a simple way will be susceptible to fluctuations, how to avoid that? Cap the weight at some value?
    # -There should be a better way to do the entries to the standings dictionary...
    def play_games_simple(self, allow_ot=True):
        for index in range(self.start, len(self.game_record)):
            self.game_record.loc[index, "game_outcome"] = random.choice(['W', 'L'])
            self.game_record.loc[index, "overtimes"] = self.overtime_check()

    # Run through the schedule and decide each game with a weighted random choice
    # Teams with greater point % are more likely to win
    # This first attempt is likely to be unstable...
    def play_games_weighted(self, allow_ot=True):
        print("not implemented.")

    def get_weight(self, game):
        print("get_weights should not be called in the base class.\n")

    def get_winner_weighted(self, game, weight):
        print("not implemented")

    # This method should contain league specific rules so it isn't implemented here in the base class
    def update_standings(self, game, winner, ot=""):
        print("update_standings should not be called from the base class.\n")

    # This method should contain league specific rules so it isn't implemented here in the base class
    def update_result(self, result):
        print("update_result should not be called from the base class.\n")

    # This method should contain league specific rules so it isn't implemented here in the base class
    def determine_playoffs(self):
        print("determine_playoffs should not be called from the base class.\n")

    # This method should contain league specific rules so it isn't implemented here in the base class
    def chk_tiebreaks(self, standings_sorted):
        print("chk_tiebreaks should not be called from the base class.\n")

    # This method should change depending on league specific rules so it isn't implemented here in the base class
    def chk_head_to_head(self, team1, team2):
        print("chk_head_to_head should not be called from the pass class.\n")

    # This method will always return an empty string (regulation win) and should be re-implemented in daughter classes
    @staticmethod
    def overtime_check():
        return ""

    # Format of the standings may change from league to league so this is not implemented in the base class
    @staticmethod
    def generate_initial_standings(teams):
        print("generate_initial_standings should not be called from the base class.\n")

    # Format of the standings may change from league to league so this is not implemented in the base class
    @staticmethod
    def generate_standings_from_game_record(teams, game_record, end=None):
        print("generate_standings_from_game_record should not be called from the base class.\n")

    # Format of the result may change from league to league so this is not implemented in the base class
    @staticmethod
    def prep_sim_result(teams):
        print("prep_sim_result should not be called from the base class.\n")

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

    # Utility function to swap elements in a tuple
    @staticmethod
    def swap_tuple_elements(tup, i, j):
        tmp = list(tup)
        tmp[i], tmp[j] = tmp[j], tmp[i]
        return tuple(tmp)

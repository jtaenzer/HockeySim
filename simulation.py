from __future__ import division
import sys
import datetime
import pandas
import numpy

from play_season_nhl import PlaySeasonNHL


class Simulation:

    def __init__(self, iterations, db, league, year, season_start="auto"):

        # Number of times to play the season
        self.iterations = iterations

        # MySQL database
        self.db = db
        # The year as a string
        self.year = str(year)
        # For now the only supported league is "nhl" and it is only used to set Ngames
        # Could be used for more in the future
        self.league = league

        if self.league == "nhl":
            self.season_obj = PlaySeasonNHL
            self.Ngames = 82
        else:  # this if-else sequence basically does nothing for now
            print("%s is not supported as a league" % self.league)
            print("Using default settings with league=\"nhl\", this may break the schedule maker")
            self.league = "nhl"
            self.season_obj = PlaySeasonNHL
            self.Ngames = 82

        # The schedule will be stored in a sql table named with format league_schedule_year
        self.schedule_name = league + "_schedule_" + self.year
        # The league structure will be stored in a sql table named with format league_structure_year
        self.structure_name = league + "_structure_" + self.year
        # The results of each iteration will be stored in a sql table with format league_season_result_year
        self.season_name = league + "_season_result_" + self.year
        # The results of the simulation will be stored in a sql table with format league_sim_result
        self.result_name = league + "_sim_result"

        # Generate a list of teams from the structure table
        self.db.cursor.execute("SELECT long_name FROM %s" % self.structure_name)
        self.teams = [team[0] for team in self.db.cursor.fetchall()]

        # This will "DELETE" the contents of the sim_result table and re-populate it with team names and 0s
        self.season_obj.generate_initial_standings(self.teams, self.result_name, self.db)

        self.season_start_date = ""
        if season_start == "full":
            # We're playing the full season, retrieve the date of the first game and assign to season_start_date
            self.db.cursor.execute("SELECT date_game FROM %s ORDER BY date_game LIMIT 1" % self.schedule_name)
            self.season_start_date = self.db.cursor.fetchone()[0]
        elif season_start == "auto":
            # Commented code below achieves the same result using JOINs and UNIONs
            # No longer necessary now that game_outcome is stored in the schedule tables
            """
            # Get list of team names so we can access all of the relevant gamelog tables
            self.db.cursor.execute("SELECT short_name FROM nhl_structure_%s" % year)
            teams_list = [team for tup in self.db.cursor.fetchall() for team in tup]
            sql_exec_str = ""
            # Building a massive sql command to do the following:
            # Inner join the schedule with a gamelog table keeping game (dates) where there is no outcome, i.e. unplayed
            # Union all of these inner joins, ordered by date_game, to get earliest date where there are unplayed games
            for index, team in enumerate(teams_list):
                team = team.lower()
                sql_exec_str += "SELECT DISTINCT sched.date_game FROM {0} sched INNER JOIN ".format(self.schedule_name)
                sql_exec_str += "nhl_gamelog_{0} {0} ON sched.date_game = {0}.date_game AND {0}.game_outcome = '' ".format(team)
                if index < len(teams_list)-1:
                    sql_exec_str += "UNION "
                else:
                    sql_exec_str += "ORDER BY date_game"
            self.db.cursor.execute(sql_exec_str)
            """
            self.db.cursor.execute("SELECT date_game FROM %s WHERE game_outcome = '' LIMIT 1" % self.schedule_name)
            try:
                self.season_start_date = self.db.cursor.fetchone()[0]
            # If there are no unplayed games we should get a TypeError (fetchone will return None)
            # IndexError should only happen if fetchall is used but include it just in case
            except (IndexError, TypeError):
                print("Couldn't find an unplayed game in %s so season_start = \"auto\" cannot be used, exiting."
                      % self.schedule_name)
                sys.exit(2)
        else:
            self.season_start_date = season_start
            # Check that season_start is a date with the correct format
            try:
                datetime.datetime.strptime(self.season_start_date, '%Y-%m-%d')
            # TypeError -> season_start isn't a string, ValueError -> season_start isn't a string with Y-m-d format
            except (TypeError, ValueError) as err:
                print(err)
                print("season_start (%s) must be auto, full, or a date with format Y-m-d, exiting." % season_start)
                sys.exit(2)
            # Check that there are games in the schedule *after* season_start
            # ***May also want to check that there are no unplayed games before season_start***
            self.db.cursor.execute("SELECT COUNT(*) FROM %s WHERE date_game >= '%s'"
                                   % (self.schedule_name, self.season_start_date))
            if self.db.cursor.fetchone()[0] < 1:
                print("Couldn't find any games in %s after season_start = %s, exiting."
                      % (self.schedule_name, self.season_start_date))
                sys.exit(2)

            self.db.cursor.execute("SELECT COUNT(*) FROM %s WHERE date_game < '%s' AND game_outcome = ''"
                                   % (self.schedule_name, self.season_start_date))
            if self.db.cursor.fetchone()[0] > 0:
                print("There are unplayed games in %s prior to %s, exiting."
                      % (self.schedule_name, self.season_start_date))
                sys.exit(2)

    def run_simulation(self):
        # Extract the schedule as a pandas data frame
        game_record = pandas.read_sql_query("SELECT * FROM %s ORDER BY date_game" % self.schedule_name, self.db.db)
        # Determine the index of the first game to simulate using self.season_start_date
        start_index = game_record.index[game_record['date_game'] == self.season_start_date].tolist()[0]
        # Create a season object
        season = PlaySeasonNHL(self.teams, game_record, start_index)
        # Fill the nhl season results table using the existing game record (up to self.season_start_date)
        season.generate_standings_from_game_record(self.teams, self.season_name, self.db, game_record, start_index)

        print("Running simulation with %i iterations" % self.iterations)

        """
        # set up progress bar
        toolbar_width = 100
        # Make sure the number of iterations is a multiple of 100
        if self.iterations % toolbar_width != 0:
            self.iterations -= self.iterations % toolbar_width
        sys.stdout.write("Progress: [%s]" % (" " * toolbar_width))
        sys.stdout.flush()
        sys.stdout.write("\b" * (toolbar_width+1))  # return to start of line, after '['
        """

        for i in range(self.iterations):
            season.play_games_simple()  # This will fill the season.game_record dataframe
            # Re-make the season result table
            season.generate_standings_from_game_record(self.teams, self.season_name, self.db, game_record)
            # Fill the "playoffs" column in the season results table
            season.determine_playoffs(self.db, self.structure_name, self.season_name)
            # Add the contents of the season results table to the sim resuls table
            season.update_result(self.db, self.result_name, self.season_name)

            """
            # Update the progress bar
            if i % (self.iterations/toolbar_width) == 0:
                sys.stdout.write("-")
                sys.stdout.flush()
            """

        self.db.table_rows("nhl_sim_result")

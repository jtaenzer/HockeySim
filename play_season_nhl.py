from __future__ import division
from play_season import PlaySeason
import random


class PlaySeasonNHL(PlaySeason):

    def __init__(self, teams, game_record, start):
        PlaySeason.__init__(self, teams, game_record, start)
        self.div_cutoff = 3  # Number of teams from each division that make the playoffs
        self.wc_cutoff = 2  # Number of teams from each conference that make the playoffs as wildcards

    # Returns "50" i.e. a coin flip for now
    def get_weight(self):
        return 50

    # Determine which teams made the playoffs based on the NHL wildcard format -- valid for 2014 onwards
    # Tie-breaking based on points, ROW are implemented
    # Tie-breaking based on head-to-head record, goal differential is not implemented, requires more thought
    def determine_playoffs(self, db, structure_name, season_name):
        db.cursor.execute("SELECT DISTINCT division FROM {0}".format(structure_name))
        divisions = [div[0] for div in db.cursor.fetchall()]
        db.cursor.execute("SELECT DISTINCT conference FROM {0}".format(structure_name))
        conferences = [conf[0] for conf in db.cursor.fetchall()]

        # Can the two separate SQL queries in this loop be combined into one?
        for div in divisions:
            db.cursor.execute("SELECT DISTINCT seas.team_name FROM {0} seas INNER JOIN {1} struct "
                              "ON seas.team_name = struct.long_name AND struct.division = '{2}' "
                              "ORDER BY seas.points DESC, seas.points_ROW DESC LIMIT {3}"
                              .format(season_name, structure_name, div, self.div_cutoff))
            playoff_teams = tuple(team[0] for team in db.cursor.fetchall())
            db.cursor.execute("UPDATE {0} SET playoffs = 1 WHERE team_name IN ('{1}')"
                              .format(season_name, "', '".join(playoff_teams)))

        # Can the two separate SQL queries in this loop be combined into one?
        for conference in conferences:
            db.cursor.execute("SELECT DISTINCT seas.team_name FROM {0} seas INNER JOIN {1} struct ON "
                              "seas.team_name = struct.long_name AND struct.conference = '{2}' AND seas.playoffs = 0 "
                              "ORDER BY seas.points DESC, seas.points_ROW DESC LIMIT {3}"
                              .format(season_name, structure_name, conference, self.wc_cutoff))
            playoff_teams = tuple(team[0] for team in db.cursor.fetchall())
            db.cursor.execute("UPDATE {0} SET playoffs = 1 WHERE team_name IN ('{1}')"
                              .format(season_name, "', '".join(playoff_teams)))

    # Update the sim result table in the database
    @staticmethod
    def update_result(db, sim_name, season_name):
        db.cursor.execute("DESCRIBE {0}".format(sim_name))
        cols = [col[0] for col in db.cursor.fetchall()]
        set_str = ", ".join(["sim.{0} = sim.{0} + seas.{0}".format(col) for col in cols[1:]])
        db.cursor.execute("UPDATE {0} sim, {1} seas SET {2} WHERE sim.team_name = seas.team_name"
                          .format(sim_name, season_name, set_str))

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

    @staticmethod
    def generate_initial_standings(teams, result_table, db):
        db.table_delete(result_table)
        db.cursor.execute("DESCRIBE {0}".format(result_table))
        cols = [col[0] for col in db.cursor.fetchall()]
        for team in teams:
            db.cursor.execute("INSERT INTO {0} ({1}) VALUES ({2})"
                              .format(result_table,
                                      ", ".join(cols),
                                      "'{0}',".format(team) + ", ".join("0"*(len(cols)-1))))

    @staticmethod
    def generate_standings_from_game_record(teams, result_table, db, game_record, end=0):
        PlaySeasonNHL.generate_initial_standings(teams, result_table, db)
        if not end:
            end = len(game_record)
        for i in range(end):
            winner = game_record.home_team_name.iloc[i]
            loser = game_record.visitor_team_name.iloc[i]
            points_row = 1
            ot_loss = 0
            if game_record.game_outcome.iloc[i] == "L":
                winner = game_record.visitor_team_name.iloc[i]
                loser = game_record.home_team_name.iloc[i]
            if game_record.overtimes.iloc[i] == 'OT':
                ot_loss = 1
            elif game_record.overtimes.iloc[i] == 'SO':
                points_row = 0
                ot_loss = 1
            db.cursor.execute("UPDATE {0} SET wins=wins+1, points=points+2, points_ROW=points_ROW+{1} "
                              "WHERE team_name='{2}'".format(result_table, points_row, winner))
            db.cursor.execute("UPDATE {0} SET losses=losses-{1}+1, OTlosses=OTlosses+{1}, points=points+{1} "
                              "WHERE team_name='{2}'".format(result_table, ot_loss, loser))

    # Can't be static because we need to know the div and wc cutoffs
    def print_result_wildcard(self, db, result_name, structure_name):
        db.cursor.execute("DESCRIBE {0}".format(result_name))
        cols = [col[0] for col in db.cursor.fetchall()]
        cols_str = "{:<25}".format(cols[0]) + " " \
                   + "".join(["{:<10}".format(col.replace("points_ROW", "ROW")) for col in cols[1:]])
        db.cursor.execute("SELECT DISTINCT conference FROM {0}".format(structure_name))
        conferences = [conf[0].upper() for conf in db.cursor.fetchall()]

        for conf in conferences:
            print("\n{0}\n".format(conf.upper()))
            print(cols_str)
            db.cursor.execute("SELECT DISTINCT division FROM {0} WHERE conference = '{1}'"
                              .format(structure_name, conf))
            divisions = [div[0].upper() for div in db.cursor.fetchall()]
            conf_playoff_teams = []
            for div in divisions:
                db.cursor.execute("SELECT DISTINCT res.team_name FROM {0} res INNER JOIN {1} struct "
                                  "ON res.team_name = struct.long_name AND struct.division = '{2}' "
                                  "AND struct.conference = '{3}' ORDER BY res.points DESC, res.points_ROW DESC "
                                  "LIMIT {4}".format(result_name, structure_name, div, conf, self.div_cutoff))
                div_playoff_teams = [team[0] for team in db.cursor.fetchall()]
                conf_playoff_teams.extend(div_playoff_teams)
                db.cursor.execute("SELECT * FROM {0} WHERE team_name IN ('{1}') ORDER BY points DESC, points_ROW DESC"
                                  .format(result_name, "', '".join(div_playoff_teams)))
                print("-----------------------------------------------------------------------------------------------")
                print("{0}".format(div.upper()))
                print("-----------------------------------------------------------------------------------------------")
                for row in db.cursor.fetchall():
                    print("{:<25}".format(row[0]) + " " + "".join(["{:<10}".format(str(val)) for val in row[1:]]))
            db.cursor.execute("SELECT DISTINCT res.team_name FROM {0} res INNER JOIN {1} struct "
                              "ON res.team_name = struct.long_name AND struct.conference = '{3}' "
                              "ORDER BY res.points DESC, res.points_ROW DESC "
                              .format(result_name, structure_name, div, conf, self.div_cutoff))
            conf_teams = [team[0] for team in db.cursor.fetchall()]
            db.cursor.execute("SELECT * FROM {0} WHERE team_name in ('{1}') and team_name NOT in ('{2}') "
                              "ORDER BY points DESC, points_ROW DESC"
                              .format(result_name, "', '".join(conf_teams), "', '".join(conf_playoff_teams)))
            print("-----------------------------------------------------------------------------------------------")
            print("WILDCARD")
            print("-----------------------------------------------------------------------------------------------")
            for row in db.cursor.fetchall():
                print("{:<25}".format(row[0]) + " " + "".join(["{:<10}".format(str(val)) for val in row[1:]]))
        print()

    @staticmethod
    def print_result_division(db, result_name, structure_name):
        db.cursor.execute("DESCRIBE {0}".format(result_name))
        cols = [col[0] for col in db.cursor.fetchall()]
        cols_str = "{:<25}".format(cols[0]) + " " \
                   + "".join(["{:<10}".format(col.replace("points_ROW", "ROW")) for col in cols[1:]])
        db.cursor.execute("SELECT DISTINCT division FROM {0}".format(structure_name))
        divisions = [div[0].upper() for div in db.cursor.fetchall()]
        for div in divisions:
            print("\n{0}\n".format(div))
            print(cols_str)
            print("---------------------------------------------------------------------------------------------------")
            db.cursor.execute("SELECT DISTINCT res.* FROM {0} res INNER JOIN {1} struct "
                              "ON res.team_name = struct.long_name AND struct.division = '{2}' "
                              "ORDER BY res.points DESC, res.points_ROW DESC"
                              .format(result_name, structure_name, div))
            for row in db.cursor.fetchall():
                print("{:<25}".format(row[0]) + " " + "".join(["{:<10}".format(str(val)) for val in row[1:]]))
        print()

    @staticmethod
    def print_result_conference(db, result_name, structure_name):
        db.cursor.execute("DESCRIBE {0}".format(result_name))
        cols = [col[0] for col in db.cursor.fetchall()]
        cols_str = "{:<25}".format(cols[0]) + " " \
                   + "".join(["{:<10}".format(col.replace("points_ROW", "ROW")) for col in cols[1:]])
        db.cursor.execute("SELECT DISTINCT conference FROM {0}".format(structure_name))
        conferences = [conf[0].upper() for conf in db.cursor.fetchall()]

        for conf in conferences:
            print("\n{0}\n".format(conf))
            print(cols_str)
            print("---------------------------------------------------------------------------------------------------")
            db.cursor.execute("SELECT DISTINCT res.* FROM {0} res INNER JOIN {1} struct "
                              "ON res.team_name = struct.long_name AND struct.conference = '{2}' "
                              "ORDER BY res.points DESC, res.points_ROW DESC"
                              .format(result_name, structure_name, conf))
            for row in db.cursor.fetchall():
                print("{:<25}".format(row[0]) + " " + "".join(["{:<10}".format(str(val)) for val in row[1:]]))
        print()

    @staticmethod
    def print_result_league(db, result_name):
        print("\nNHL\n")
        db.cursor.execute("DESCRIBE {0}".format(result_name))
        cols = [col[0] for col in db.cursor.fetchall()]
        print("{:<25}".format(cols[0]) + " "
              + "".join(["{:<10}".format(col.replace("points_ROW", "ROW")) for col in cols[1:]]))
        print("-------------------------------------------------------------------------------------------------------")
        db.cursor.execute("SELECT * FROM {0} ORDER BY points DESC, points_ROW DESC".format(result_name))
        for row in db.cursor.fetchall():
            print("{:<25}".format(row[0]) + " " + "".join(["{:<10}".format(str(val)) for val in row[1:]]))
        print()

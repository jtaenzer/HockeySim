import pandas as pd
import numpy as np


class DataPipeline:

    def __init__(self, dbmaker):
        self.dbmaker = dbmaker
        self.db = dbmaker.db
        self.cursor = dbmaker.cursor

    def dataframe_from_sql_table(self, table_name, variables=[]):
        var_str = ", ".join(variables) + ", " + output
        if not variables:
            var_str = "*"
        return pd.read_sql_query("SELECT {0} FROM {1}".format(var_str, table_name))

    def create_average_game_data_table(self, league, teams_dict, variables, step=5):
        schedule_table = "{0}_schedule".format(league)
        schedule_df = pd.read_sql_query("SELECT * FROM {0} WHERE game_outcome != ''".format(schedule_table), self.db)
        schedule_df["game_outcome"] = np.where(schedule_df["game_outcome"] == 'W', 1, 0)

        home_vars = ["home_" + var + "_avg" for var in variables]
        away_vars = ["away_" + var + "_avg" for var in variables]
        variables_str = ", ".join(variables)
        insert_list = []
        for index, row in schedule_df.iterrows():
            date_game = row["date_game"]
            home_table = "nhl_gamelog_{0}".format(teams_dict[row["home_team_name"]])
            away_table = "nhl_gamelog_{0}".format(teams_dict[row["visitor_team_name"]])
            home_data = pd.read_sql_query("SELECT {0} FROM {1} WHERE date_game < '{2}' "
                                          "ORDER BY date_game DESC LIMIT {3}"
                                          .format(variables_str, home_table, row["date_game"], str(step)), self.db)
            away_data = pd.read_sql_query("SELECT {0} FROM {1} WHERE date_game < '{2}' "
                                          "ORDER BY date_game DESC LIMIT {3}"
                                          .format(variables_str, away_table, row["date_game"], str(step)), self.db)
            home_averages = []
            away_averages = []
            for var in variables:
                home_averages.append(np.sum(home_data[var])/step)
                away_averages.append(np.sum(away_data[var])/step)
            game_list = [date_game, row["home_team_name"], row["visitor_team_name"], row["game_outcome"]]
            game_list.extend(home_averages)
            game_list.extend(away_averages)
            insert_list.append(game_list)

        output_table_name = "{0}_avgdata_N{1}".format(league, str(step))
        columns_str = "(date_game DATE, home_team_name VARCHAR(255), visitor_team_name VARCHAR(255), game_outcome INT, " \
                    "{0} FLOAT, {1} FLOAT)".format(" FLOAT, ".join(home_vars), " FLOAT, ".join(away_vars))

        # Try to create the table in case it doesn't already exist
        self.dbmaker.table_create(output_table_name, columns_str)
        # Delete any existing data from the table
        self.dbmaker.table_delete(output_table_name)
        insert_str = "INSERT IGNORE INTO {0} (date_game, home_team_name, visitor_team_name, game_outcome, {1}, {2}) " \
                     "VALUES ({3})".format(output_table_name,
                                           ", ".join(home_vars),
                                           ", ".join(away_vars),
                                           ", ".join(["%s"] * len(insert_list[0])))
        self.cursor.executemany(insert_str, insert_list)
        self.db.commit()

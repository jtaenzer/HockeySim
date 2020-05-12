import pandas as pd
import numpy as np


class DataPipeline:

    def __init__(self, db):
        self.db = db

    def extract_data(self, table_name, step=5, variables=[], output="game_outcome"):
        var_str = ", ".join(variables) + ", " + output
        cols = variables
        if not variables:
            var_str = "*"
            self.db.cursor.execute("DESCRIBE {0}".format(table_name))
            cols = [col[0] for col in self.db.cursor.fetchall()]

        gamelog = pd.read_sql_query("SELECT {0} FROM {1} WHERE game_outcome != ''".format(var_str, table_name),
                                    self.db.db)

        data_list = []
        for i in range(1, len(gamelog)):
            averages = []
            for col in cols:
                if i < step:
                    averages.append(np.sum(gamelog[col].iloc[0:i])/i)
                else:
                    averages.append(np.sum(gamelog[col].iloc[i-step:i])/step)
            data_list.append(averages)
            data_list[-1].append(gamelog[output].iloc[i])
        return pd.DataFrame(np.array(data_list), columns=variables + [output])

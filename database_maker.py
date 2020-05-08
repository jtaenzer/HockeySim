import sys
import mysql.connector
import requests
import pandas as pd
from bs4 import BeautifulSoup


# This class now contains some NHL specific methods, at some point these should be split into a daughter class
class DatabaseMakerMySQL:

    def __init__(self, host, user, passwd, database_name=None):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.database_name = database_name

        self.db = None
        self.cursor = None
        if not database_name:
            self.db = self.mysql_connect()
        else:
            self.db = self.db_connect()

        if self.db:
            self.cursor = self.db.cursor(buffered=True)

    # Connect to mySQL without a database, called from init if no database name is provided
    def mysql_connect(self):
        try:
            db = mysql.connector.connect(
                host=self.host,
                user=self.user,
                passwd=self.passwd,
            )
            return db
        except:
            err = sys.exc_info()[0]
            print("Couldn't connect to mySQL %s : ", err)
        return None

    # Connect to mySQL with a database, called from init
    def db_connect(self):
        try:
            db = mysql.connector.connect(
                host=self.host,
                user=self.user,
                passwd=self.passwd,
                database=self.database_name
            )
            return db
        except:
            err = sys.exc_info()[0]
            print("Couldn't connect to database %s : " % self.database_name, err)
        return None

    # Create a new database
    def db_create(self, database_name):
        try:
            self.cursor.execute("CREATE DATABASE %s" % database_name)
        except mysql.connector.errors.DatabaseError as err:
            print(err)

    # Drop a database USE WITH CAUTION
    def db_drop(self, database_name):
        try:
            self.cursor.execute("DROP DATABASE IF EXISTS %s" % database_name)
        except mysql.connector.errors.ProgrammingError as err:
            print(err)

    # Create a new table
    def table_create(self, table_name, columns_str):
        try:
            self.cursor.execute("CREATE TABLE " + table_name + " " + columns_str)
        except mysql.connector.errors.ProgrammingError as err:
            print(err)

    # Drop a table
    def table_drop(self, table_name):
        try:
            self.cursor.execute("DROP TABLE IF EXISTS %s" % table_name)
        except mysql.connector.errors.ProgrammingError as err:
            print(err)

    # Check if a table exists
    def table_exists(self, table_name):
        self.cursor.execute("SHOW TABLES LIKE '%s'" % table_name)
        # This will return 'None' if the table doesn't exist
        if self.cursor.fetchone():
            return True
        return False

    # Print rows for debugging
    def table_rows(self, table_name, order_by=""):
        sql_str = "SELECT * FROM " + table_name
        if order_by:
            sql_str = sql_str + " ORDER BY " + order_by
        self.cursor.execute(sql_str)
        for row in self.cursor.fetchall():
            print(row)

    def table_length(self, table_name):
        sql_str = "SELECT * FROM " + table_name
        self.cursor.execute(sql_str)
        print("%s contains %s rows." % (table_name, len(self.cursor.fetchall())))

    # This functionality exists in pandas already and is probably done better there, could be deprecated?
    # Some issues:
    # No protection against non-csv files
    # Assumes either all columns will be used or any columns to be dropped are at the end of each row
    # Assumes there is no column of row numbers in the csv file
    # Assumes first row is column names
    def insert_from_csv(self, table_name, file_path, col_names=""):
        # Start of the SQL command, modified later
        sql_str = "INSERT IGNORE INTO " + table_name
        # Loop over the lines in the csv file
        table_list = []  # List which will hold rows of the table
        for cnt, line in enumerate(open(file_path, "r")):
            # First line has to be the column names or else this will skip data...
            if cnt == 0:
                if col_names:
                    num_columns = len(col_names.split(","))
                else:
                    num_columns = len(line.split(",")) + 1
                    col_names = "rownum, " + line.replace("\n", "")  # Insert row numbers since we assume there are none
                # Rest of the SQL command is determined here based on column names and number of columns
                sql_str = sql_str + " (" + col_names + ") VALUES (" + ("%s, " * num_columns)[:-2] + ")"
                continue
            line = line.replace("\n", "")
            values = line.split(",")
            values.insert(0, cnt)  # Insert row number into values at the front
            table_list.append(values[:num_columns])  # Strip unused columns at the end
        self.cursor.executemany(sql_str, table_list)
        self.db.commit()
        print(self.cursor.rowcount, "record inserted.")

    def insert_from_urls(self, table_name="", attributes=pd.DataFrame(), urls=[], tag="", tag_attrs={}):
        if not table_name:
            print("database_maker.insert_from_url: No table name provided, can't insert.")
            sys.exit(2)
        if len(urls) < 1:
            print("database_maker.insert_from_url: No URLs provided, can't insert.")
            sys.exit(2)
        if not tag:
            print("database_maker.insert_from_url: No HTML tag provided for findAll, can't insert.")
            sys.exit(2)
        if len(attributes) < 1:
            print("database_maker.insert_from_url: No table attributes provided, can't insert.")
            sys.exit(2)

        sql_str = "INSERT IGNORE INTO %s (%s) VALUES (%s)" \
                  % (table_name, ", ".join(attributes['attr']), ("%s"*len(attributes['attr'])).replace("s%", "s, %"))

        for url in urls:
            try:
                page = requests.get(url)
            except requests.exceptions.MissingSchema as err:
                print("database_maker.insert_from_url: %s" % err)
                sys.exit(2)
            soup = BeautifulSoup(page.content, "html.parser")
            insert_list = []
            for line_index, line in enumerate(soup.findAll(tag, attrs=tag_attrs)):
                missing_val = False
                val_list = []
                for row_index, row in attributes.iterrows():
                    attr = row['attr']
                    children = line.findChildren(row['tag'], attrs={'data-stat': attr})
                    if len(children) == 0:
                        missing_val = True
                    elif len(children) > 1:
                        print("database_maker.insert_from_url: "
                              "Ambiguous attribute (%s) found multiple children on page (%s), exiting." % (attr, url))
                        sys.exit(2)
                    else:
                        val_list.append(children[0].text)
                if missing_val:
                    continue
                insert_list.append(tuple(val_list))
            self.cursor.executemany(sql_str, insert_list)
            self.db.commit()
            print("Inserted %s rows into %s" % (str(self.cursor.rowcount), table_name))

    # Merge a list of tables provided in table_list into another table (mod_table)
    # Use new=True if mod_table doesn't already exist
    # Currently no protection against attempting to merge tables with inconsistent columns
    def merge_tables(self, mod_table, table_list, selection="*", new=False):
        if new:
            self.cursor.execute("CREATE TABLE %s AS SELECT %s FROM %s" % (mod_table, selection, table_list[0]))
            self.db.commit()
            print("Inserted %s rows into %s" % (str(self.cursor.rowcount), mod_table))
            table_list.pop(0)
        for table in table_list:
            self.cursor.execute("INSERT IGNORE INTO %s SELECT %s FROM %s" % (mod_table, selection, table))
            self.db.commit()
            print("Inserted %s rows into %s" % (str(self.cursor.rowcount), mod_table))

    @staticmethod
    def table_str_from_df(attributes=pd.DataFrame()):
        table_str = "("
        for index, row in attributes.iterrows():
            table_str += row['attr'] + " " + row['type'] + ", "
        return table_str[:-2] + ")"

    # This method is a hack to get the NHL conference/division structure year by year
    # Ideally should be replaced something more general
    def insert_league_structure_table(self, table_name, attributes, teams_dict, url, tag="table", tag_attrs={}):
        try:
            page = requests.get(url)
        except requests.exceptions.MissingSchema as err:
            print("database_maker.insert_league_structure_table: %s" % err)
            sys.exit(2)
        soup = BeautifulSoup(page.content, "html.parser")
        sql_str = "INSERT IGNORE INTO %s (%s) VALUES (%s)" \
                  % (table_name, ", ".join(attributes['attr']), ("%s"*len(attributes['attr'])).replace("s%", "s, %"))
        insert_list = []
        for line_index, line in enumerate(soup.findAll(tag, attrs=tag_attrs)):
            for div_index, div in enumerate(line.findChildren("tr")):
                val_list = []
                division = ""
                if 'class' in div.attrs.keys() and 'thead' in div.attrs['class']:
                    division = div.text.split(" ")[0].lower()
                for team_index, team in enumerate(div.findChildren("th", attrs={'data-stat': 'team_name'})):
                    if team.text:
                        # Remove special characters (mostly the * used to indicate a team made the playoffs)
                        import re
                        team_clean = re.sub('[^a-zA-Z0-9 \n\.]', '', team.text)
                        if not division:
                            print("database_maker.insert_league_structure_table: "
                                  "Division not found for team %s in table %s, something went wrong"
                                  % (team_clean, table_name))
                            sys.exit(2)
                        val_list.extend([team_clean, teams_dict[team_clean], division, "conf"])
                if len(val_list) > 0:
                    insert_list.append(val_list)
        self.cursor.executemany(sql_str, insert_list)
        self.db.commit()
        print("Inserted %s rows into %s" % (str(self.cursor.rowcount), table_name))

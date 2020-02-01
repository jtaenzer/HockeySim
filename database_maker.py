import sys
import mysql.connector

class database_maker:

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
            self.cursor = self.db.cursor()

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
            self.cursor.execute("CREATE DATABASE " + database_name)
        except mysql.connector.errors.DatabaseError as err:
            print(database_name + " DB already exists,", err)

    # Create a new table
    def table_create(self, table_name, columns_str):
        try:
            self.cursor.execute("CREATE TABLE " + table_name + " " + columns_str)
        except mysql.connector.errors.ProgrammingError as err:
            print("hockeydatabase.nhl_teams table may already exist,", err)

    # Drop a table
    def table_drop(self, table_name):
        try:
            self.cursor.execute("DROP TABLE " + table_name)
        except mysql.connector.errors.ProgrammingError as err:
            print("Couldn't drop table " + table_name, err)

    # This functionality exists in pandas already and is probably done better there, could be deprecated?
    # Some issues:
    # No protection against non-csv files
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
            values = line.strip(",").split(",")  # Is the .strip even necessary here?
            values.insert(0, cnt)  # Insert row number into values at the front
            table_list.append(values[:num_columns])
        self.cursor.executemany(sql_str, table_list)
        self.db.commit()
        print(self.cursor.rowcount, "record inserted.")

    # Print rows for debugging
    def table_rows(self, table_name):
        self.cursor.execute("SELECT * FROM " + table_name)
        for row in self.cursor.fetchall():
            print(row)

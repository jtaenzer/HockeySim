import sys
import getopt
from database_maker import DatabaseMakerMySQL


def help():
    print("help")


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hl:u:p:d:", ["help", "host=", "user=", "passwd=", "database="])
    except getopt.GetoptError:
        help()
        sys.exit(2)
    host = None
    user = None
    passwd = None
    database_name = None
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            help()
            sys.exit()
        elif opt in ("-l", "--host"):
            host = arg
        elif opt in ("-u", "--user"):
            user = arg
        elif opt in ("-p", "--passwd"):
            passwd = arg
        elif opt in ("-d", "--database"):
            database_name = arg

    if None not in (host, user, passwd, database_name):
        pass
    else:
        help()
        sys.exit(2)

    db = DatabaseMakerMySQL(host, user, passwd)
    db.db_create(database_name)
    db = DatabaseMakerMySQL(host, user, passwd, database_name)

    db.table_create("nhl_teams",
                    "(rownum INT, \
                    team_name VARCHAR(255) PRIMARY KEY, \
                    division VARCHAR(255), \
                    conference VARCHAR(255))")
    db.insert_from_csv("nhl_teams", "./teams/NHL_2018-2019.txt")

    db.table_create("nhl_schedule_2018",
                    "(game_id INT PRIMARY KEY, \
                    datecolumn DATETIME, \
                    visitor VARCHAR(255), \
                    visitor_goals INT, \
                    home VARCHAR(255), \
                    home_goals INT, \
                    ot VARCHAR(255))")
    db.insert_from_csv("nhl_schedule_2018", "./schedules/NHL_2018-2019.csv",
                       col_names = "game_id, datecolumn, visitor, visitor_goals, home, home_goals, ot")

    db.table_create("nhl_schedule_2019",
                    "(game_id INT PRIMARY KEY, \
                    datecolumn DATETIME, \
                    visitor VARCHAR(255), \
                    visitor_goals INT, \
                    home VARCHAR(255), \
                    home_goals INT, \
                    ot VARCHAR(255))")
    db.insert_from_csv("nhl_schedule_2019", "./schedules/NHL_2019-2020.csv",
                       col_names="game_id, datecolumn, visitor, visitor_goals, home, home_goals, ot")

    db.table_create("nhl_result",
                    "(rownum INT, \
                    team_name VARCHAR(255) PRIMARY KEY, \
                    playoffs INT, wins INT, losses INT, otlosses INT, points INT, rowval INT)")


if __name__ == "__main__":
    main()

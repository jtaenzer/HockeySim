import sys
import getopt

from database_maker import DatabaseMakerMySQL
from simulation import Simulation


def print_help():
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
            print_help()
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
        print_help()
        sys.exit(2)

    db = DatabaseMakerMySQL(host, user, passwd, database_name)
    sim = Simulation(1, db, "nhl", 2020, "auto")
    sim.run_simulation()


if __name__ == "__main__":
    main()

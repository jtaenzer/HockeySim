import sys
import getopt
import requests
import pandas as pd
import dbconfig as dbcfg
from database_maker import DatabaseMakerMySQL
from bs4 import BeautifulSoup

# Finds the date the playoffs started for a particular season
# Used to mark playoff games in the db
def find_playoffs_start_date(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find("table", attrs={"id": "games_playoffs"})
    # This will throw an AttributeError if the playoff table doesn't exist
    try:
        date = table.findChild("th", attrs={"data-stat": "date_game", "scope": "row"}).text
    except AttributeError:
        return False
    # Make sure we actually retrieved a date!
    from dateutil.parser import parse
    try:
        parse(date, fuzzy=False)
        return date
    except ValueError:
        return False


def print_help():
    print("Usage:")
    print("python build_db_nhl.py -h <host> -u <user> -p <passwd> -d <database_name>")
    print("e.g. python build_db_nhl.py -h localhost -u joe -p passwd -d nhldb")
    sys.exit()


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hl:u:p:d:", ["help", "host=", "user=", "passwd=", "database="])
    except getopt.GetoptError:
        print_help()
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

    db = DatabaseMakerMySQL(host, user, passwd)
    if dbcfg.remake_db:
        db.db_drop(database_name)
        db.db_create(database_name)
    db = DatabaseMakerMySQL(host, user, passwd, database_name)

    if dbcfg.remake_league_structure_tables:
        table_name = "nhl_structure"
        structure_attrs = pd.DataFrame(dbcfg.structure_attrs, columns=['attr', 'tag', 'type'])
        table_str = db.table_str_from_df(structure_attrs)
        for year in dbcfg.years:
            structure_url = "https://www.hockey-reference.com/leagues/NHL_%s.html" % year
            db.table_drop(table_name + "_%s" % year)
            db.table_create(table_name + "_%s" % year, table_str)
            db.insert_league_structure_table(table_name + "_%s" % year, structure_attrs, dbcfg.teams_dict,
                                             structure_url, tag="table",
                                             tag_attrs={"id": ["standings_EAS", "standings_WES"]})
            db.cursor.execute("SELECT long_name, division FROM nhl_structure_%s" % year)
            for row in db.cursor.fetchall():
                long_name = row[0]
                division = row[1]
                if division in dbcfg.eastern_conf:
                    db.cursor.execute("UPDATE nhl_structure_%s SET conference = '%s' WHERE long_name = '%s'"
                                      % (year, "eastern", long_name))
                elif division in dbcfg.western_conf:
                    db.cursor.execute("UPDATE nhl_structure_%s SET conference = '%s' WHERE long_name = '%s'"
                                      % (year, "western", long_name))
        db.db.commit()  # Not sure why this is necessary in this particular case

    if dbcfg.remake_schedule_tables:
        table_name = "nhl_schedule"
        schedule_attrs = pd.DataFrame(dbcfg.schedule_attrs, columns=['attr', 'tag', 'type'])
        table_str = db.table_str_from_df(schedule_attrs)
        schedule_urls = []
        for year in dbcfg.years:
            schedule_urls.append("https://www.hockey-reference.com/leagues/NHL_%s_games.html" % year)
            db.table_drop(table_name + "_%s" % year)  # Probably needs protection against the table not existing
            db.table_create(table_name + "_%s" % year, table_str)
            db.insert_from_urls(table_name + "_%s" % year, schedule_attrs, [schedule_urls[-1]], tag="tr")
            playoff_start_date = find_playoffs_start_date(schedule_urls[-1])
            if not playoff_start_date:
                playoff_start_date = "2100-01-01"
            db.cursor.execute("ALTER TABLE %s_%s ADD game_outcome VARCHAR (255)" % (table_name, year))
            db.cursor.execute("UPDATE %s_%s SET game_outcome = CASE "
                              "WHEN (home_goals > visitor_goals) THEN 'W' "
                              "WHEN (home_goals < visitor_goals) THEN 'L' "
                              "WHEN (home_goals = '' OR visitor_goals = '' OR home_goals = visitor_goals) THEN '' "
                              "END" % (table_name, year))
            db.cursor.execute("ALTER TABLE %s_%s ADD playoff_game INT" % (table_name, year))
            db.cursor.execute("UPDATE %s_%s SET playoff_game = IF(date_game >= '%s', 1, 0)"
                              % (table_name, year, playoff_start_date))
        db.table_drop(table_name)  # Probably needs protection against the table not existing
        db.merge_tables(table_name, ["nhl_schedule_%s" % year for year in dbcfg.years], new=True)

    if dbcfg.fill_gamelog_tables:
        gamelog_attrs = pd.DataFrame(dbcfg.gamelog_attrs, columns=['attr', 'tag', 'type'])
        table_str = db.table_str_from_df(gamelog_attrs)
        for team in dbcfg.teams:
            table_name = "nhl_gamelog_%s" % team
            gamelog_urls = []
            for year in dbcfg.years:
                team_url = team
                if team == "ARI" and int(year) < 2015:
                    team_url = "PHX"
                if team == "WPG" and int(year) < 2012:
                    team_url = "ATL"
                gamelog_urls.append("https://www.hockey-reference.com/teams/%s/%s_gamelog.html" % (team_url, year))
            if dbcfg.remake_gamelog_tables:
                db.table_drop(table_name)
                db.table_create(table_name, table_str)
            db.insert_from_urls(table_name, gamelog_attrs, gamelog_urls, tag='tr',
                                tag_attrs={'id': [lambda x: x.startswith('tm_gamelog_')]})

    if dbcfg.remake_sim_result_table:
        sim_result_attrs = pd.DataFrame(dbcfg.sim_result_attrs, columns=['attr', 'tag', 'type'])
        table_str = db.table_str_from_df(sim_result_attrs)
        table_name = "nhl_sim_result"
        db.table_drop(table_name)
        db.table_create(table_name, table_str)

    if dbcfg.remake_season_result_tables:
        season_result_attrs = pd.DataFrame(dbcfg.sim_result_attrs, columns=['attr', 'tag', 'type'])
        table_str = db.table_str_from_df(season_result_attrs)
        for year in dbcfg.years:
            table_name = "nhl_season_result_%s" % year
            db.table_drop(table_name)
            db.table_create(table_name, table_str)


if __name__ == "__main__":
    main()

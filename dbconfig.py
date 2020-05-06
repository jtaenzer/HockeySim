remake_db = False
remake_league_structure_tables = False
remake_schedule_tables = False
fill_gamelog_tables = False
remake_gamelog_tables = False

years = ['2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020']


teams = ['PIT', 'WSH', 'PHI', 'CAR', 'NYI', 'CBJ', 'NYR', 'NJD', 'BOS', 'TBL', 'TOR', 'FLA', 'BUF', 'MTL', 'OTT', 'DET',
         'STL', 'DAL', 'COL', 'WPG', 'NSH', 'MIN', 'CHI', 'EDM', 'VEG', 'VAN', 'CGY', 'ARI', 'SJS', 'ANA', 'LAK']

structure_attrs = [['long_name', '', 'VARCHAR (255) PRIMARY KEY'],
                   ['short_name', '', 'VARCHAR (255)'],
                   ['division', '', 'VARCHAR (255)'],
                   ['conference', '', 'VARCHAR (255)']]

schedule_attrs = [['date_game', 'th', 'DATE'],
                  ['visitor_team_name', 'td', 'VARCHAR (255)'],
                  ['home_team_name', 'td', 'VARCHAR (255)']]

gamelog_attrs = [['date_game', 'td', 'DATE PRIMARY KEY'],
                 ['opp_name', 'td', 'VARCHAR(255)'],
                 ['goals', 'td', 'INT'],
                 ['opp_goals', 'td', 'INT'],
                 ['game_outcome', 'td', 'INT'],
                 ['overtimes', 'td', 'VARCHAR(255)'],
                 ['shots', 'td', 'INT'],
                 ['pen_min', 'td', 'INT'],
                 ['goals_pp', 'td', 'INT'],
                 ['chances_pp', 'td', 'INT'],
                 ['goals_sh', 'td', 'INT'],
                 ['shots_against', 'td', 'INT'],
                 ['pen_min_opp','td', 'INT'],
                 ['goals_against_pp', 'td', 'INT'],
                 ['opp_chances_pp', 'td', 'INT'],
                 ['goals_against_sh', 'td', 'INT'],
                 ['corsi_for', 'td', 'INT'],
                 ['corsi_against', 'td', 'INT'],
                 ['corsi_pct', 'td', 'FLOAT'],
                 ['fenwick_for', 'td', 'INT'],
                 ['fenwick_against', 'td', 'INT'],
                 ['fenwick_pct', 'td', 'FLOAT'],
                 ['faceoff_wins', 'td', 'INT'],
                 ['faceoff_losses', 'td', 'INT'],
                 ['faceoff_percentage', 'td', 'FLOAT'],
                 ['zs_offense_pct', 'td', 'FLOAT'],
                 ['pdo', 'td', 'FLOAT']]

teams = {'Tampa Bay Lightning': 'TBL',
         'Boston Bruins': 'BOS',
         'Toronto Maple Leafs': 'TOR',
         'Montreal Canadiens': 'MTL',
         'Florida Panthers': 'FLA',
         'Buffalo Sabres': 'BUF',
         'Detroit Red Wings': 'DET',
         'Ottawa Senators': 'OTT',
         'Washington Capitals': 'WSH',
         'New York Islanders': 'NYI',
         'Pittsburgh Penguins': 'PIT',
         'Carolina Hurricanes': 'CAR',
         'Columbus Blue Jackets': 'CBJ',
         'Philadelphia Flyers': 'PHI',
         'New York Rangers': 'NYR',
         'New Jersey Devils': 'NJD',
         'Winnipeg Jets': 'WPG',
         'Atlanta Thrashers': 'WPG',  # The Thrashers moved to Winnipeg at the start of the 2012 season
         'Nashville Predators': 'NSH',
         'St. Louis Blues': 'STL',
         'Dallas Stars': 'DAL',
         'Minnesota Wild': 'MIN',
         'Chicago Blackhawks': 'CHI',
         'Colorado Avalanche': 'COL',
         'Calgary Flames': 'CGY',
         'San Jose Sharks': 'SJS',
         'Las Vegas Golden Knights': 'VEG',
         'Vegas Golden Knights': 'VEG',  # Data is inconsistent about Las Vegas vs. Vegas
         'Arizona Coyotes': 'ARI',
         'Phoenix Coyotes': 'ARI',  # The Coyotes changed their name from Phoenix to Arizona in 2015
         'Edmonton Oilers': 'EDM',
         'Vancouver Canucks': 'VAN',
         'Anaheim Ducks': 'ANA',
         'Los Angeles Kings': 'LAK'}

eastern_conf = ["atlantic", "metropolitan", "northeast", "southeast"]
western_conf = ["central", "pacific", "northwest"]
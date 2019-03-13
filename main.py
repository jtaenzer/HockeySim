import operator
import schedule as sched
import games as games


def print_standings_sorted(standings):
  standings_sorted = sorted(standings.items(), key=lambda kv: kv[1]['points'], reverse=True)
  print '{:<25}'.format('Team'), '{:<10}'.format('Wins'), '{:<10}'.format('Losses'), '{:<10}'.format('OT Losses'), '{:<10}'.format('Points')
  for team in xrange(len(standings_sorted)): 
    print '{:<25}'.format(standings_sorted[team][0]), '{:<10}'.format(standings_sorted[team][1]["wins"]), '{:<10}'.format(standings_sorted[team][1]["losses"]), '{:<10}'.format(standings_sorted[team][1]["OTlosses"]), '{:<10}'.format(standings_sorted[team][1]["points"])

teams_file = open("teams.txt","r")
teams = []
for line in teams_file: teams.append(line.replace("\n",""))

schedule = sched.generate_schedule_simple(teams, 82)
standings = games.play_games_simple(teams, schedule)
print_standings_sorted(standings)

"""
for i in range(1000):
  print "running iteration :", i
  standings = games.play_games_simple(teams, schedule)
"""



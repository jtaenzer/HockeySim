from __future__ import division

import operator
import schedule as sched
import games as games


def print_standings_sorted(standings):
  standings_sorted = sorted(standings.items(), key=lambda kv: kv[1]['points'], reverse=True)
  print '{:<25}'.format('Team'), '{:<10}'.format('Wins'), '{:<10}'.format('Losses'), '{:<10}'.format('OT Losses'), '{:<10}'.format('Points')
  for team in xrange(len(standings_sorted)): 
    print '{:<25}'.format(standings_sorted[team][0]), '{:<10}'.format(standings_sorted[team][1]["wins"]), '{:<10}'.format(standings_sorted[team][1]["losses"]), '{:<10}'.format(standings_sorted[team][1]["OTlosses"]), '{:<10}'.format(standings_sorted[team][1]["points"])

def prep_sim_dict(teams):
  result = {}
  for team in teams: result[team]=0
  return result

# Read teams from file
teams_file = open("teams.txt","r")
teams = []
for line in teams_file: teams.append(line.replace("\n",""))

# Make the result dictionary based on the teams
result=prep_sim_dict(teams)

iterations = 1000
Ngames = 82
cutoff = 16

# Prepare a (random) schedule for the season
#schedule = sched.generate_schedule_simple(teams, Ngames)

# Import schedule from file
schedule = sched.import_schedule_csv("/home/joe/Desktop/fun/HockeySim/schedules/NHL_2018-2019.csv")
if not sched.chk_schedule_simple(teams,schedule,Ngames): print "Imported schedule failed sanity check."

else:
# Run iterations of the same season
  for i in range(iterations):
    #if i%1000==0: print "Running iteration :", i
    standings = games.play_games_simple(teams, schedule)
    standings_sorted = sorted(standings.items(), key=lambda kv: kv[1]['points'], reverse=True)
    for j in xrange(cutoff): result[standings_sorted[j][0]]+=1

  for team in result: 
    odds=100*result[team]/iterations
    print "%s %.2f" % ('{:<25}'.format(team), odds)

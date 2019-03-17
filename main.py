from __future__ import division

import operator
import schedule as sched
import games as games

# Print sorted standings, for debugging
def print_standings_sorted(standings):
  standings_sorted = sorted(standings.items(), key=lambda kv: (kv[1]['points'], kv[1]['ROW']), reverse=True)
  print '{:<25}'.format('Team'), '{:<10}'.format('Wins'), '{:<10}'.format('Losses'), '{:<10}'.format('OT Losses'), '{:<10}'.format('Points'), '{:<10}'.format('ROW') 
  for team in xrange(len(standings_sorted)):
    if team==cutoff: print "----------------"
    print '{:<25}'.format(standings_sorted[team][0]), '{:<10}'.format(standings_sorted[team][1]["wins"]), '{:<10}'.format(standings_sorted[team][1]["losses"]), '{:<10}'.format(standings_sorted[team][1]["OTlosses"]), '{:<10}'.format(standings_sorted[team][1]["points"]), '{:<10}'.format(standings_sorted[team][1]["ROW"])

# Print the result dictionary
def print_sim_result(result):
  print "%s %s" % ('{:<25}'.format('Team'), 'Playoff %')
  for team in result: 
    odds=100*result[team]/iterations
    print "%s %.2f" % ('{:<25}'.format(team), odds)
  print ''

# Create an empty dictionary to hold the simulated result
# For now the result is just the count of how many times each team makes the playoffs
def prep_sim_result(teams):
  result = {}
  for team in teams: result[team]=0
  return result

# Simple determination of which teams made the playoffs just by taking the top N teams in the standings dict
# Cutoff establishes the number of teams to include
# Tie-break based on ROW (assumes NHL rules)
def determine_playoffs_simple(standings, result, cutoff=16):
  teams_in=0
  standings_sorted = sorted(standings.items(), key=lambda kv: (kv[1]['points'], kv[1]['ROW']), reverse=True)
  for i in xrange(len(standings_sorted)):
    if teams_in >= cutoff: continue
    else:
      result[standings_sorted[i][0]]+=1
      teams_in+=1

# Determine which teams made the playoffs based on the NHL wildcard format
# Tie-breaking based on ROW is implemented
# Tie-breaking based on head-to-head games and goals scored not implemented. Not clear how to do this yet.
#determine_playoffs_NHL(standings, result):

##############################

# Read teams from file
teams_file = open("/home/joe/Desktop/fun/HockeySim/teams/NHL_2018-2019.txt","r")
teams = []
for line in teams_file: teams.append(line.replace("\n",""))

sims = 1
iterations = 500
Ngames = 82
cutoff = 16

# Prepare a (random) schedule for the season
#schedule = sched.generate_schedule_simple(teams, Ngames)
#if not schedule: print "Failed to create a random schedule."

# Import schedule from file
schedule = sched.import_schedule_csv("/home/joe/Desktop/fun/HockeySim/schedules/NHL_2018-2019.csv")
if not sched.chk_schedule_simple(teams,schedule,Ngames): print "Imported schedule failed sanity check."

else:
# Run iterations of the same season
  for sim in xrange(sims):
    print "Running sim #", sim
    print ''
    # Make the result dictionary based on the teams
    result=prep_sim_result(teams)

    for i in xrange(iterations):
      #if i%1000==0: print "Running iteration :", i
      standings = games.play_games_simple(teams, schedule)
#      print_standings_sorted(standings)
      determine_playoffs_simple(standings, result, cutoff)

    print_sim_result(result)

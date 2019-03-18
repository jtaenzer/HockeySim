from __future__ import division

import random
import operator
import schedule as sched
import games as games
import sorting as sort
from visualize import visualize

# Print sorted standings, for debugging
def print_standings_sorted(standings):
  standings_sorted = sort_by_points_row(standings)
  print '{:<25}'.format('Team'), '{:<10}'.format('Wins'), '{:<10}'.format('Losses'), '{:<10}'.format('OT Losses'), '{:<10}'.format('Points'), '{:<10}'.format('ROW') 
  for team in xrange(len(standings_sorted)):
    if team==cutoff: print "----------------"
    print '{:<25}'.format(standings_sorted[team][0]), '{:<10}'.format(standings_sorted[team][1]["wins"]), '{:<10}'.format(standings_sorted[team][1]["losses"]), '{:<10}'.format(standings_sorted[team][1]["OTlosses"]), '{:<10}'.format(standings_sorted[team][1]["points"]), '{:<10}'.format(standings_sorted[team][1]["ROW"])

# Print the result dictionary
def print_sim_result(result, quantity, mult=100):
  print "%s %s" % ('{:<25}'.format('Team'), quantity)
  for team in result: 
    mult_quantity=mult*result[team]/iterations
    print "%s %.2f" % ('{:<25}'.format(team), mult_quantity)
  print ''

# Create an empty dictionary to hold the simulated result
# For now the result is just the count of how many times each team makes the playoffs
# Maybe this should be moved?
def prep_sim_result(teams):
  result = {}
  for team in teams: result[team]=0
  return result

##############################

# Read teams from file
file_path = "/home/joe/Desktop/fun/HockeySim/teams/NHL_2018-2019.txt"
teams_file = open(file_path,"r")
teams = []
for line in teams_file: teams.append(line.split(',')[0])

sims = 25
iterations = 1000
Ngames = 82
cutoff = 16
rootfile="test.root"
treename="tree"

# Prepare a (random) schedule for the season
#schedule = sched.generate_schedule_simple(teams, Ngames)
#if not schedule: print "Failed to create a random schedule."

# Import schedule from file
schedule = sched.import_schedule_csv("/home/joe/Desktop/fun/HockeySim/schedules/NHL_2018-2019.csv")
if not sched.chk_schedule_simple(teams,schedule,Ngames): print "Imported schedule failed sanity check."

else:

  plotter = visualize(rootfile,treename, teams)
  plotter.set_weight(100/iterations)

# Run iterations of the same season
  for sim in xrange(sims):
    print "Running sim #", sim
    print ''
    # Make the result dictionary based on the teams
    result=prep_sim_result(teams)

    for i in xrange(iterations):
      game_record = games.play_games_simple(schedule)
      standings = games.generate_standings_from_game_record(file_path,game_record)
      sort.determine_playoffs_simple_NHL(game_record, standings, result, cutoff)
      #sort.determine_playoffs_simple(game_record, standings, result, cutoff)

    # Only print the sim results if we ran multiple iterations
    if iterations>1: 
      print_sim_result(result, "Playoff %")
      plotter.fill_TTree(sim, result)

plotter.write_TFile()
#plotter.draw_TGraphs()

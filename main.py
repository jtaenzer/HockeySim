from __future__ import division

import random

from simulation import simulation
from schedule_maker import schedule_maker
from play_season import play_season
from visualize import visualize

##############################

# Read teams from file
teams_file = "/home/joe/Desktop/fun/HockeySim/teams/NHL_2018-2019.txt"
schedule_file="/home/joe/Desktop/fun/HockeySim/schedules/NHL_2018-2019.csv"

sims = 2
iterations = 1000
doPlotting=True
rootfile="test.root"
treename="tree"

sim = simulation(iterations, "NHL", teams_file, schedule_file)

if doPlotting:
  plotter = visualize(rootfile,treename,sim.teams)
  plotter.set_weight(100/iterations)

for i in xrange(sims):
  sim.run_simulation()
  if doPlotting:
    plotter.fill_TTree(i, sim.result)

plotter.write_TFile()
#plotter.draw_TGraphs()

"""

schedmaker = schedule_maker("NHL", teams, Ngames, schedule_file)
if not schedmaker.schedule: print "Schedule is empty"


else:



# Run iterations of the same season
  for sim in xrange(sims):
    print "Running sim #", sim
    print ''
    # Make the result dictionary based on the teams
    result=prep_sim_result(teams)

    for i in xrange(iterations):
      season_18_19 = play_season(file_path, schedmaker.schedule)
      season_18_19.play_games_simple()
      season_18_19.determine_playoffs_NHL(result)

    # Only print the sim results if we ran multiple iterations
    if iterations>1: 
      print_sim_result(result, "Playoff %")
      plotter.fill_TTree(sim, result)

plotter.write_TFile()
#plotter.draw_TGraphs()
"""

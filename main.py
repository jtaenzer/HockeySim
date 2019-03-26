from __future__ import division

from simulation import Simulation
from visualize import Visualize

##############################

# Read teams from file


sims          = 1
iterations    = 1000
teams_file    = "/home/joe/Desktop/fun/HockeySim/teams/NHL_2018-2019.txt"
schedule_file = "/home/joe/Desktop/fun/HockeySim/schedules/NHL_2018-2019.csv"
season_start  = 0

doPlotting = True
rootfile   = "test.root"
treename   = "tree"

sim = Simulation(iterations, "NHL", teams_file, schedule_file, season_start)
plotter = None

team_names = []
for team in sim.teams:
    team_names.append(team.name)

if doPlotting:
    plotter = Visualize(rootfile, treename, team_names)
    plotter.set_weight(100/iterations)

for i in xrange(sims):
    sim.run_simulation()
    if doPlotting:
        plotter.fill_TTree(i, sim.result)

plotter.write_TFile()
#plotter.draw_TGraphs()

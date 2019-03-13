import random

# Create a dictionary to hold wins, losses, OT losses for each team
def generate_initial_standings(teams):
  standings = {}
  for team in teams:
    standings[team] = {"wins":0, "losses":0, "OTlosses":0, "points":0}
  return standings

# Decide if a game went to overtime assuming 25% of games go to OT
def overtime_check():
  if random.randint(0,3) < 3: return False
  return True

# Flip a coin
def coin_flip():
  return random.randint(0,1)

# Under construction, flip a coin but weight the results
def weighted_coin_flip(weight1,weight2):
  return random.randint(0,weight1+weight2) > weight1

# Run through the schedule and decide each game with a coin flip
# Ideas/thoughts:
# -Use a weighted coin flip instead, take weights for each team as an input
# -Modify the initial weight based on each teams record
#  Doing this in a simple way will be susceptible to fluctuations, how to avoid that? Cap the weight at some value?
# -There should be a better way to do the entries to the standings dictionary...
def play_games_simple(teams, schedule):
  standings = generate_initial_standings(teams)
  for day in schedule:
    for game in schedule[day]:
      winner=coin_flip()
      OT=overtime_check()
      if winner==0: 
        standings[game[0]]["wins"]+=1; standings[game[0]]["points"]+=2
        if OT: standings[game[1]]["OTlosses"]+=1; standings[game[1]]["points"]+=1
        else:  standings[game[1]]["losses"]+=1        
      elif winner==1:
        standings[game[1]]["wins"]+=1; standings[game[1]]["points"]+=2
        if OT: standings[game[0]]["OTlosses"]+=1; standings[game[0]]["points"]+=1
        else:  standings[game[0]]["losses"]+=1
  return standings


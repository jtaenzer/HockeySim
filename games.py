import random

# Create a dictionary to hold wins, losses, OT losses for each team
def generate_initial_standings(teams):
  standings = {}
  for team in teams:
    standings[team] = {"wins":0, "losses":0, "OTlosses":0, "points":0, "ROW":0}
  return standings

# Decide if a game went to overtime assuming 25% of games go to OT
def overtime_check():
  result = random.randint(0,100)
  # Approximate numbers stolen from an article about 3on3 OT
  # Regulation - 75%, OT - 15%, SO - 10%
  if result >= 90: return "SO"
  elif result < 90 and result >= 75: return "OT"
  else: return "REG"


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
      winner=random.choice(game)
      OT=overtime_check()
      for team in game:
        if team==winner:
          standings[team]["wins"]+=1; standings[team]["points"]+=2
          if OT=="REG" or OT=="OT": standings[team]["ROW"]+=1
        else:
          if OT=="REG": standings[team]["losses"]+=1
          if OT=="OT" or OT=="SO": standings[team]["OTlosses"]+=1; standings[team]["points"]+=1 
  return standings

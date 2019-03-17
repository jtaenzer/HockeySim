import random, copy

# Create a dictionary to hold wins, losses, OT losses for each team
def generate_initial_standings(teams_file_path):
  standings = {}
  teams_file = open(teams_file_path,'r')
  for line in teams_file:
    line_mod = line.replace('\n','')
    standings[line_mod.split(',')[0]] = {"wins":0, "losses":0, "OTlosses":0, "points":0, "ROW":0, "div":line_mod.split(',')[1]}
  return standings


def generate_standings_from_game_record(teams_file_path, game_record):

  standings = generate_initial_standings(teams_file_path)
  for game in game_record:
    winner=game_record[game]["winner"]
    if game_record[game]["visitor"] == winner: loser=game_record[game]["home"]
    else: loser=game_record[game]['visitor']
    standings[winner]["wins"]+=1
    standings[winner]["points"]+=2
    # This bit isn't great, hard coding and probably not optimal
    OT=game_record[game]["OT"]
    if OT=="REG":
      standings[winner]["ROW"]+=1
      standings[loser]["losses"]+=1
    elif OT=="OT":
      standings[winner]["ROW"]+=1
      standings[loser]["points"]+=1
      standings[loser]["OTlosses"]+=1
    elif OT=="SO":
      standings[loser]["points"]+=1
      standings[loser]["OTlosses"]+=1

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
def play_games_simple(schedule, allowOT=True):
  game_record = copy.deepcopy(schedule)
  for day in game_record:
    game = [schedule[day]['visitor'], schedule[day]['home']]
    winner = random.choice(game)
    game_record[day].update({'winner':winner})
    if allowOT: OT=overtime_check()
    else: OT="REG"
    game_record[day].update({'OT':OT})
  return game_record

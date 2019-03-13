import random
import schedule as sched

def coin_flip():
  return random.randint(0,1)

def weighted_coin_flip(weight1,weight2):
  return random.randint(0,weight1+weight2) > weight1

def generate_initial_standings(teams):
  standings = {}
  for team in teams:
    standings[team] = {"wins":0, "losses":0}
  return standings

def play_games(teams, schedule):
  standings = generate_initial_standings(teams)
  for day in schedule:
    for game in schedule[day]:
      winner=coin_flip()
      if winner==0: 
        standings[game[0]]["wins"]+=1
        standings[game[1]]["losses"]+=1
      elif winner==1:
        standings[game[1]]["wins"]+=1
        standings[game[0]]["losses"]+=1
  return standings

teams = ["Calgary","Edmonton", "San Jose", "Colorado", "Pheonix"]
schedule = sched.generate_schedule_simple(teams, 82)
standings = play_games(teams, schedule)

print "team", "wins", "losses"
for team in standings: 
  print team, standings[team]["wins"], standings[team]["losses"]

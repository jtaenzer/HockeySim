import random, copy

# Generates random games to put in the schedule
def generate_games_simple(teams):
  games = []
  # Deepcopy teams so we can remove entries as we generate games without affecting the original list
  teams_remaining = copy.deepcopy(teams)

  # Loop until there is at most 1 team remaining, in case the number of teams is uneven
  while len(teams_remaining)>1:
    home=random.choice(teams_remaining) 
    teams_remaining.remove(home)
    away=random.choice(teams_remaining)
    teams_remaining.remove(away)
    games.append([home,away])
  return teams_remaining, games

# Generates an extra game, used if there is an uneven number of teams
def generate_remainder_game_simple(remainder,teams):
  games = []
  home = remainder[0]
  teams.remove(home)
  away=random.choice(teams)
  games.append([home,away])
  return away,games

# Generate a random schedule where every team in teams will play N games
# Missing rules:
# 1. Balancing home/away games
# 2a. Ensuring each team plays each other team the same number of times
# 2b. Ensuring each team plays each other team the correct number of times
# ...Probably more
def generate_schedule_simple(teams, Ngames):
  schedule = {}
  extra = "" # extra is used to keep track of teams that have an "extra" game due to an uneven number of teams
  daycounter=1

  # Loop until the generated schedule has Ngames games for every team
  while chk_schedule_simple(teams, schedule, Ngames)==False:
    key="day"+str(daycounter) # key for the schedule dictionary

    # Deepcopy teams so we can remove entries when a remainder game is necessary
    teams_mod = copy.deepcopy(teams)

    # If extra is non-empty, we generated a remainder game in the previous iteration
    # so we remove the team that played an extra game from teams_mod
    if extra:
      teams_mod.remove(extra)
      extra = ""

    # Generate a set of games
    remainder, schedule[key] = generate_games_simple(teams_mod)

    # If remainder is non-empty, we have an uneven number of teams
    # So we generate an extra game game for the team that was left out on this iteration
    if len(remainder)>0:
      daycounter+=1
      key="day"+str(daycounter)
      extra,schedule[key]=generate_remainder_game_simple(remainder,teams_mod)
    daycounter+=1

  return schedule


# Probably could be improved / refactored
def chk_schedule_simple(teams, schedule, Ngames):

  # If schedule is empty, return False
  if not schedule: return False

  # Regenerating this dictionary every time isn't efficiency -- rethink
  team_game_counter = {}
  for team in teams: team_game_counter[team]=0

  # Count how many games each team plays in the current schedule
  for day in schedule:
    for game in schedule[day]:
      for team in teams:
        if team in game: team_game_counter[team]+=1

  # If any team doesn't have Ngames scheduled, return False
  for team in teams:
    if team_game_counter[team]!=Ngames: return False

  # If we survived the previous for loop, it should be safe to return True
  return True

# Imports a csv formatted schedule
def import_schedule_csv(filepath):

  print "importing schedule from :", filepath

  schedule = {}

  # Read schedule from file
  sched_file = open(filepath,"r")
  for line in sched_file:
    #print line.replace("\n","").split(',')
    line_split=line.replace("\n","").split(',')
    if line_split[0]=="Date": continue
    if line_split[0] not in schedule.keys(): schedule[line_split[0]]=[]
    schedule[line_split[0]].append([line_split[1],line_split[3]])

  return schedule

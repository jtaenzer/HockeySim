import random, copy

# Generate a random schedule where every team in teams will play N games
# Missing rules:
# 1. Balancing home/away games
# 2a. Ensuring each team plays each other team the same number of times
# 2b. Ensuring each team plays each other team the correct number of times (based on e.g. divisional/conference rules)
# ...Probably more
# This should only be used for debugging in its current state
def generate_schedule_simple(teams, Ngames):
  schedule = {}
  extra = "" # extra is used to keep track of teams that have an "extra" game due to an uneven number of teams
  gamecounter=0
  daycounter=0

  # Loop until the generated schedule has Ngames games for every team
  while chk_schedule_simple(teams, schedule, Ngames)==False:
    key="game"+str(daycounter) # key for the schedule dictionary

    # Deepcopy teams so we can remove entries without affecting the original list
    teams_local = copy.deepcopy(teams)

    # If extra is non-empty, we generated a remainder game in the previous iteration
    # so we remove the team that played an extra game from teams_local
    if extra:
      teams_local.remove(extra)
      extra = ""

    # Add games to schedule by choosing teams at random from teams_remaining
    # Teams chosen for games are removed from teams_remaining until at most 1 is left, which will happen if len(teams) is odd
    teams_remaining=copy.deepcopy(teams_local)
    while len(teams_remaining)>1:
      home=random.choice(teams_remaining);
      teams_remaining.remove(home)
      away=random.choice(teams_remaining);
      teams_remaining.remove(away)
      schedule["game"+str(gamecounter)]={ "date":"day"+str(daycounter), "visitor":away, "home":home }
      gamecounter+=1

    # If len(teams) is odd, we will have a "remainder" team that didn't get a game scheduled in the above while loop
    # Schedule a game for that team with  another random team
    # The team with an "extra" game will be removed from teams_local / teams_remaining in the next loop iteration
    if len(teams_remaining)>0:
      daycounter+=1
      remainder=teams_remaining[0]
      teams_local.remove(remainder)
      extra=random.choice(teams_local)
      teams_remaining.append(extra)
      home=random.choice(teams_remaining);
      teams_remaining.remove(home)
      away=random.choice(teams_remaining);
      teams_remaining.remove(away)
      schedule["game"+str(gamecounter)]={ "date":"day"+str(daycounter), "visitor":away, "home":home }
      gamecounter+=1

  return schedule

# Adapting for the new dictionary structure of the schedule
def chk_schedule_simple(teams, schedule, Ngames):

  # If schedule is empty, return False
  if not schedule: return False

  # Regenerating this dictionary every time isn't efficiency -- rethink
  team_game_counter = {}
  for team in teams: team_game_counter[team]=0

  # Count how many games each team plays in the current schedule
  for day in schedule:
    for team in teams:
      if team in schedule[day]['visitor'] or team in schedule[day]['home']: team_game_counter[team]+=1


  # If any team doesn't have Ngames scheduled, return False
  for team in teams:
    if team_game_counter[team]!=Ngames: return False

  # If we survived the previous for loop, it should be safe to return True
  return True

# Imports a csv formatted schedule
# Now records visitor and home for each game for tie-break purposes
def import_schedule_csv(filepath):

  print ''
  print "importing schedule from :", filepath
  print ''

  schedule = {}
  game_counter=0
  # Read schedule from file
  sched_file = open(filepath,"r")
  for line in sched_file:
    line_split=line.replace("\n","").split(',')
    if line_split[0]=="Date": continue
    schedule["game"+str(game_counter)] = { "date":line_split[0], "visitor":line_split[1], "home":line_split[3]}
    game_counter+=1

  return schedule

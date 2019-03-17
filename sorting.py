import random, copy

# Utility function to sort by points and ROW, since we do this alot
def sort_by_points_row(standings):
  return sorted(standings.items(), key=lambda kv: (kv[1]['points'], kv[1]['ROW']), reverse=True)

# Utility function to merge dictionaries (lol python 2)
def merge_dicts(x,y):
  z=x.copy()
  z.update(y)
  return z

# Utility function to swap elements in a tuple, used for tiebreaking
def swap_tuple_elements(tup, i, j):
  tmp=list(tup)
  tmp[i], tmp[j] = tmp[j], tmp[i]
  return tuple(tmp)

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

# Sort the standings by NHL divisions
# Used in determine_playoffs_simple_NHL()
def sort_standings_by_division_NHL(standings):
  atlantic={}
  metro={}
  central={}
  pacific={}

  for team in standings:
    if   standings[team]['div'] == 'a': atlantic[team] = standings[team]
    elif standings[team]['div'] == 'm': metro[team]    = standings[team]
    elif standings[team]['div'] == 'c': central[team]  = standings[team]
    elif standings[team]['div'] == 'p': pacific[team]  = standings[team]

  return atlantic,metro,central,pacific

# Check the head to head record for tie breaking
# Rules (per NHL.com):
# Team with that earned the most points in games between the two teams wins the tie-break
# When the teams played an odd number of games, points earned in the first game played in the city that had the extra game shall not be included.
# The last fallback if the teams are still tied is the team with the greater goal differential -- not clear what to do there, just return random for now
def chk_head_to_head(game_record, team1, team2):

  # First for convenience find the head-to-head games in our game_record and put them in a smaller dictionary
  head_to_head = {}
  for game in game_record:
    if (game_record[game]["home"] == team1 or game_record[game]["visitor"] == team1) and (game_record[game]["home"] == team2 or game_record[game]["visitor"] == team2):
      head_to_head[game]=(game_record[game])

  # For odd numbers of games, determine which team had more home games and "pop" their first home game from head_to_head
  # This could probably be improved
  if len(head_to_head)%2!=0:
    count={team1:0, team2:0}
    checked_pairs=[]
    head_to_head_sorted=sorted(head_to_head.items(), key=lambda kv: kv[1]['date'])
    for i in xrange(len(head_to_head_sorted)): count[head_to_head_sorted[i][1]["home"]]+=1
    if count[team1] > count[team2]: pop_team=team1
    else: pop_team=team2
    for i in xrange(len(head_to_head_sorted)):
      if count[head_to_head_sorted[i][1]["home"]]==pop_team: head_to_head.pop(head_to_head_sorted[i][0])

  # Determine how many points each team earned in their games against each other
  team1_pts=0
  team2_pts=0
  for game in head_to_head:
    if game_record[game]["winner"]==team1:
      team1_pts+=2
      if game_record[game]["OT"] == "OT" or game_record[game]["OT"] == "SO": team2_pts+=1
    elif game_record[game]["winner"]==team2:
      team2_pts+=2
      if game_record[game]["OT"] == "OT" or game_record[game]["OT"] == "SO": team1_pts+=1

  if team1_pts > team2_pts: return team1
  elif team2_pts < team1_pts: return team2
  else: return random.choice([team1,team2]) # If they're still tied, just return a random choice

# This method checks for ties and re-orders the standings based on tie-breakers
# For now only the head-to-head record is checked
def chk_tiebreaks(game_record, standings_sorted):

  checkedpairs=[]
  for i in xrange(len(standings_sorted)):
    for j in xrange(len(standings_sorted)):
      if i==j: continue
      if [i,j] in checkedpairs or [j,i] in checkedpairs: continue
      if standings_sorted[i][1]["points"] == standings_sorted[j][1]["points"] and standings_sorted[i][1]["ROW"] == standings_sorted[j][1]["ROW"]:
        if chk_head_to_head(game_record, standings_sorted[i][0], standings_sorted[j][0]) == standings_sorted[j][0]:
          standings_sorted=swap_tuple_elements(standings_sorted, i, j)
      checkedpairs.append([i,j])

  return standings_sorted

# Determine which teams made the playoffs based on the NHL wildcard format
# Tie-breaking based on ROW is implemented
# Tie-breaking based on head-to-head games and goals scored not implemented. Not clear how to do this yet.
def determine_playoffs_simple_NHL(game_record, standings, result, total_cutoff=16, debug=False):

  # Should these by hard coded??
  div_cutoff=3 # top 3 teams from each division automatically make the playoffs
  wildcard_cutoff=2 # After removing the div leaders, the top 2 teams from each conference take the wildcard spots

  atlantic,metro,central,pacific = sort_standings_by_division_NHL(standings)
  east=merge_dicts(atlantic,metro)
  west=merge_dicts(central,pacific)

  standings_sorted = chk_tiebreaks( game_record, sort_by_points_row(standings) )
  atlantic_sorted  = chk_tiebreaks( game_record, sort_by_points_row(atlantic) )
  metro_sorted     = chk_tiebreaks( game_record, sort_by_points_row(metro) )
  central_sorted   = chk_tiebreaks( game_record, sort_by_points_row(central) )
  pacific_sorted   = chk_tiebreaks( game_record, sort_by_points_row(pacific) )

  # This should be improved, but is good enough while tie-breaking is only points and ROW
  for i in xrange(div_cutoff):
      result[atlantic_sorted[i][0]]+=1
      result[metro_sorted[i][0]]+=1
      east.pop(atlantic_sorted[i][0]); east.pop(metro_sorted[i][0])
      result[central_sorted[i][0]]+=1
      result[pacific_sorted[i][0]]+=1
      west.pop(central_sorted[i][0]); west.pop(pacific_sorted[i][0]);

  east_sorted = chk_tiebreaks( game_record, sort_by_points_row(east) )
  west_sorted = chk_tiebreaks( game_record, sort_by_points_row(west) )

  for i in xrange(wildcard_cutoff):
    result[east_sorted[i][0]]+=1
    result[west_sorted[i][0]]+=1

  # Print the standings for debug if we only ran 1 season
  if debug:
    print 'ATLANTIC'
    print '------------------------'
    print_standings_sorted(atlantic)
    print '------------------------'
    print ''

    print 'METROPOLITAN'
    print '------------------------'
    print_standings_sorted(metro)
    print '------------------------'
    print ''

    print 'CENTRAL'
    print '------------------------'
    print_standings_sorted(central)
    print '------------------------'

    print 'PACIFIC'
    print '------------------------'
    print_standings_sorted(pacific)
    print '------------------------'
    print ''

    print 'EAST (minus division leaders)'
    print '------------------------'
    print_standings_sorted(east)
    print '------------------------'
    print ''

    print 'WEST (minus division leaders)'
    print '------------------------'
    print_standings_sorted(west)
    print '------------------------'
    print ''

# Saves the number of points from each sim in the result instead of a playoff counter
# Sanity check
def chk_points(standings, result):
  for team in standings: result[team]+=standings[team]["points"]

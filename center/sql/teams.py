user_teams = """SELECT
  user_info.leaderID,
  team.title as team_title
FROM people.team_user
  LEFT OUTER JOIN people.team
    ON team_user.teamID = team.id
  LEFT OUTER JOIN people.context_team
    ON context_team.teamID = team.id
  LEFT OUTER JOIN people.user_info
    ON team_user.userID = user_info.userID
WHERE context_team.contextID = 24
GROUP BY user_info.leaderID"""

island_users = """
   
"""

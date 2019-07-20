user_teams = """SELECT
  user_info.leaderID,
  team.id AS team_id,
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


team_count = """
SELECT
  team.id AS team_id,
  COUNT(user.id) AS team_users
FROM  people.team_user
  LEFT OUTER JOIN  people.team
    ON team_user.teamID = team.id
  LEFT OUTER JOIN  people.context_team
    ON context_team.teamID = team.id
  LEFT OUTER JOIN  people.user
    ON team_user.userID = user.id
WHERE context_team.contextID = 24
  GROUP BY team_id
"""

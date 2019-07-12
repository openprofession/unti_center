user_teams = """SELECT
  user_info.untiID,
  user_info.leaderID,
  user_info.firstname,
  user_info.lastname,
  team.title AS team_title
FROM people.user_info
  LEFT OUTER JOIN people.team_user
    ON user_info.userID = team_user.userID
  LEFT OUTER JOIN people.team
    ON team_user.teamID = team.id
  LEFT OUTER JOIN people.context_team
    ON context_team.teamID = team.id
  LEFT OUTER JOIN people.context
    ON context_team.contextID = context.id
  INNER JOIN people.user_tag
    ON user_info.userID = user_tag.userID
  INNER JOIN people.tag
    ON user_tag.tagID = tag.id

AND context_team.contextID = 24
GROUP BY untiID"""

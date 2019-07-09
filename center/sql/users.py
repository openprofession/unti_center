users_participant = ''''''

users_active_lk_today = '''SELECT COUNT(DISTINCT result.untiID) FROM
((SELECT
  user.loginDT,
  user.activeDT,
  user_info.untiID,
  user_info.leaderID,
  tag.title
FROM xle.user_info
  RIGHT OUTER JOIN xle.user
    ON user_info.userID = user.id
  LEFT OUTER JOIN xle.user_tag
    ON user_tag.userID = user.id
  LEFT OUTER JOIN xle.tag
    ON user_tag.tagID = tag.id
WHERE tag.title = '1022-verified-participant-final'
AND user.activeDT >= CURDATE())

UNION
  (SELECT
  user.loginDT,
  user.activeDT,
  user_info.untiID,
  user_info.leaderID,
  tag.title
FROM now.user_info
  RIGHT OUTER JOIN now.user
    ON user_info.userID = user.id
  LEFT OUTER JOIN now.user_tag
    ON user_tag.userID = user.id
  LEFT OUTER JOIN now.tag
    ON user_tag.tagID = tag.id
WHERE tag.title = '1022-verified-participant-final'
AND user.activeDT >= CURDATE())) AS result'''

users_active_lk_all = '''SELECT COUNT(DISTINCT result.untiID) FROM
((SELECT
  user.loginDT,
  user.activeDT,
  user_info.untiID,
  user_info.leaderID,
  tag.title
FROM xle.user_info
  RIGHT OUTER JOIN xle.user
    ON user_info.userID = user.id
  LEFT OUTER JOIN xle.user_tag
    ON user_tag.userID = user.id
  LEFT OUTER JOIN xle.tag
    ON user_tag.tagID = tag.id
WHERE tag.title = '1022-verified-participant-final'
AND user.activeDT >= '2019-07-08')

UNION
  (SELECT
  user.loginDT,
  user.activeDT,
  user_info.untiID,
  user_info.leaderID,
  tag.title
FROM now.user_info
  RIGHT OUTER JOIN now.user
    ON user_info.userID = user.id
  LEFT OUTER JOIN now.user_tag
    ON user_tag.userID = user.id
  LEFT OUTER JOIN now.tag
    ON user_tag.tagID = tag.id
WHERE tag.title = '1022-verified-participant-final'
AND user.activeDT > '2019-07-08')) AS result'''

users_active_mob_today = """SELECT
  COUNT(DISTINCT user_ip.userID) AS expr1
FROM now.user_ip
  RIGHT OUTER JOIN now.user_tag
    ON user_ip.userID = user_tag.userID
WHERE user_ip.contextID = 30
AND user_tag.tagID = 103
AND user_ip.createDT > CURDATE()"""

users_active_mob_all = """SELECT
  COUNT(DISTINCT user_ip.userID) AS expr1
FROM now.user_ip
  RIGHT OUTER JOIN now.user_tag
    ON user_ip.userID = user_tag.userID
WHERE user_ip.contextID = 30
AND user_tag.tagID = 103
AND user_ip.createDT > '2019-07-08'"""

users_island_tag = '''SELECT
  user_info.untiID,
  user_info.leaderID,
  user_info.firstname,
  user_info.lastname,
  user_info.middlename,
  tag.title AS tag_title
FROM ple.user_info
  INNER JOIN ple.user_tag
    ON user_info.userID = user_tag.userID
  INNER JOIN ple.tag
    ON user_tag.tagID = tag.id
WHERE tag.title = "1022-verified-participant-final"'''

users_island_tag_count = '''SELECT COUNT(user_info.untiID) as user_count
FROM ple.user_info
  INNER JOIN ple.user_tag
    ON user_info.userID = user_tag.userID
  INNER JOIN ple.tag
    ON user_tag.tagID = tag.id
WHERE tag.title = "1022-verified-participant-final"'''

users_team_tag_long = """SELECT
  user_info.untiID,
  user_info.leaderID,
  user_info.firstname,
  user_info.lastname,
  user_info.middlename,
  GROUP_CONCAT(team.title) AS team_titles,
  team_user.teamID,
  tag.title
FROM people.user_info
  LEFT OUTER JOIN people.team_user
    ON user_info.userID = team_user.userID
  LEFT OUTER JOIN people.team
    ON team_user.teamID = team.id
  LEFT OUTER JOIN ple.user_info user_info_1
    ON user_info.untiID = user_info_1.untiID
  LEFT OUTER JOIN ple.user_tag
    ON user_info_1.userID = user_tag.userID
  LEFT OUTER JOIN ple.tag
    ON user_tag.tagID = tag.id
WHERE tag.title = '1022-verified-participant'
AND team.title IS NOT NULL
GROUP BY user_info.untiID"""

users_registered = """SELECT
leader_isledashboard.regdt,
leader_isledashboard.regflag,
leader_isledashboard.fullname,
leader_isledashboard.deal_id,
leader_isledashboard.contact_id,
leader_isledashboard.leader_id
FROM leader_crm.leader_isledashboard
WHERE leader_isledashboard.regflag IS NOT NULL"""

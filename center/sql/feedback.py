aim_all = """
SELECT
  aim.uuid,
  aim.text AS aim_text,
  aim.createDT AS aim_createDT,
  aim_feedback.rating,
  aim_feedback.text AS feedback_text,
  aim_feedback.createDT AS feedback_createDT,
  user_info.untiID,
  user_info.leaderID 
FROM now.aim_feedback
  RIGHT OUTER JOIN now.aim
    ON aim_feedback.aimID = aim.id
  LEFT OUTER JOIN now.user_info
    ON aim.userID = user_info.userID
"""


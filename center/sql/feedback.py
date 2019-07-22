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

event_feedback_rating = """
SELECT
  concat(user_info.leaderID, "_", event.uuid) AS user_event,
  user_feedback_answer.value
FROM xle.user_feedback_answer
  LEFT OUTER JOIN xle.event
    ON user_feedback_answer.eventID = event.id
  LEFT OUTER JOIN xle.timeslot
    ON event.timeslotID = timeslot.id
  LEFT OUTER JOIN xle.user_info
    ON user_feedback_answer.userID = user_info.userID
  LEFT OUTER JOIN xle.feedback_question
    ON user_feedback_answer.feedbackQuestionID = feedback_question.id
WHERE feedback_question.type = 'rating'
GROUP BY user_event"""

event_feedback_rating_aggr = """
SELECT
  event.uuid AS event_uuid,
  event.title,
  COUNT(user_info.leaderID) AS feedback_users_count,
  MIN(user_feedback_answer.value) AS min_score,
  MAX(user_feedback_answer.value) AS max_score,
  AVG(user_feedback_answer.value) AS avg_score
FROM xle.user_feedback_answer
  LEFT OUTER JOIN xle.event
    ON user_feedback_answer.eventID = event.id
  LEFT OUTER JOIN xle.timeslot
    ON event.timeslotID = timeslot.id
  LEFT OUTER JOIN xle.user_info
    ON user_feedback_answer.userID = user_info.userID
  LEFT OUTER JOIN xle.feedback_question
    ON user_feedback_answer.feedbackQuestionID = feedback_question.id
WHERE feedback_question.type = 'rating'
  GROUP BY event_uuid
"""

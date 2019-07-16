sport_rate = """
SELECT
  user_feedback_answer.*,
  event.title,
  user_info.leaderID,
  user_info.untiID
FROM user_feedback_answer
  LEFT OUTER JOIN event
    ON user_feedback_answer.eventID = event.id
  LEFT OUTER JOIN user_info
    ON user_feedback_answer.userID = user_info.userID
WHERE user_feedback_answer.feedbackQuestionID = 13
"""

sport_selfie = """
SELECT
  user_feedback_answer.*,
  event.title,
  user_info.leaderID,
  user_info.untiID
FROM user_feedback_answer
  LEFT OUTER JOIN event
    ON user_feedback_answer.eventID = event.id
  LEFT OUTER JOIN user_info
    ON user_feedback_answer.userID = user_info.userID
WHERE user_feedback_answer.feedbackQuestionID = 14
"""

sport_tracker = """
SELECT
  user_feedback_answer.*,
  event.title,
  user_info.leaderID,
  user_info.untiID
FROM user_feedback_answer
  LEFT OUTER JOIN event
    ON user_feedback_answer.eventID = event.id
  LEFT OUTER JOIN user_info
    ON user_feedback_answer.userID = user_info.userID
WHERE user_feedback_answer.feedbackQuestionID = 15
"""

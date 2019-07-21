sport_enrolls_all = """
SELECT
  user_info.leaderID,
  user_info.untiID,
  user_info.firstname,
  user_info.lastname,
  date(timetable.dt) AS eventDT,
  timetable.type,
  event.title,
  event.id AS event_id,
  event.uuid as event_uuid,
  activity.sizeMin,
  activity.sizeMax,
  CONCAT(event.id,'_',user_info.untiID) AS event_user,
  CONCAT(date(timetable.dt),'_',user_info.untiID) AS date_user
FROM xle.timetable
  LEFT OUTER JOIN xle.event
    ON timetable.runID = event.runID
  LEFT OUTER JOIN xle.run
    ON event.runID = run.id
  LEFT OUTER JOIN xle.activity
    ON run.activityID = activity.id
  LEFT OUTER JOIN xle.activity_type
    ON activity.id = activity_type.activityID
  LEFT OUTER JOIN xle.user_info
    ON timetable.userID = user_info.userID
WHERE activity_type.typeID = 192
group by date_user
"""

sport_attendance_all = """
SELECT
  user_info.leaderID,
  user_info.untiID,
  event.id AS event_id,
  event.uuid as event_uuid,
  user_feedback_answer.value,
  CONCAT(event.id,'_',user_info.untiID) AS event_user
FROM xle.user_feedback_answer
  LEFT OUTER JOIN xle.event
    ON user_feedback_answer.eventID = event.id
  LEFT OUTER JOIN xle.timeslot
    ON event.timeslotID = timeslot.id
  LEFT OUTER JOIN xle.user_info
    ON user_feedback_answer.userID = user_info.userID
  LEFT OUTER JOIN xle.feedback_question
    ON user_feedback_answer.feedbackQuestionID = feedback_question.id
  LEFT OUTER JOIN xle.run
    ON event.runID = run.id
  INNER JOIN xle.activity
    ON run.activityID = activity.id
  LEFT OUTER JOIN xle.activity_type
    ON activity_type.activityID = activity.id
WHERE activity_type.typeID = 192 AND feedback_question.type = 'rating'
group by event_user
"""

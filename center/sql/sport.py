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
  activity.sizeMin,
  activity.sizeMax
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
"""

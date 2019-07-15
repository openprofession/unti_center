sport_events_by_date = """
SELECT
  event.title,
  timeslot.startDT,
  timeslot.endDT,
  activity.requestType,
  type.title,
  event.id,
  event.uuid,
  activity.sizeMin,
  activity.sizeMax
FROM xle.event
  LEFT OUTER JOIN xle.run
    ON event.runID = run.id
  LEFT OUTER JOIN xle.context_run
    ON run.id = context_run.runID
  LEFT OUTER JOIN xle.timeslot
    ON event.timeslotID = timeslot.id
  LEFT OUTER JOIN xle.activity
    ON run.activityID = activity.id
  LEFT OUTER JOIN xle.activity_type
    ON activity.id = activity_type.activityID
  LEFT OUTER JOIN xle.type
    ON activity_type.typeID = type.id
WHERE context_run.contextID = 30
AND type.id = 192
AND date(timeslot.endDT) = '2019-07-11'
GROUP BY event.id"""

events_enroll_by_date_type = """
SELECT
  timetable.userID,
  timetable.dt,
  timetable.type,
  event.title,
  event.id AS event_id,
  timetable.createDT,
  activity.sizeMin,
  activity.sizeMax
FROM xle.timetable
  LEFT OUTER JOIN xle.event
    ON timetable.runID = event.runID
  LEFT OUTER JOIN xle.run
    ON event.runID = run.id
  LEFT OUTER JOIN xle.activity
    ON run.activityID = activity.id
WHERE event.id IN (SELECT
    event.id
  FROM xle.event
    LEFT OUTER JOIN xle.run
      ON event.runID = run.id
    LEFT OUTER JOIN xle.context_run
      ON run.id = context_run.runID
    LEFT OUTER JOIN xle.timeslot
      ON event.timeslotID = timeslot.id
    LEFT OUTER JOIN xle.activity
      ON run.activityID = activity.id
    LEFT OUTER JOIN xle.activity_type
      ON activity.id = activity_type.activityID
    LEFT OUTER JOIN xle.type
      ON activity_type.typeID = type.id
  WHERE (context_run.contextID = 30
  AND event.isDeleted <> 1
  AND type.id = %s
  AND date(timeslot.endDT) = %s)
  GROUP BY event.id)
"""

enrolls_auction_2 = """
SELECT
  timetable.userID,
  timetable.dt,
  timetable.type,
  event.title,
  event.id AS event_id,
  timetable.createDT,
  activity.sizeMin,
  activity.sizeMax,
  place.title AS place_title
FROM xle.timetable
  LEFT OUTER JOIN xle.event
    ON timetable.runID = event.runID
  LEFT OUTER JOIN xle.run
    ON event.runID = run.id
  LEFT OUTER JOIN xle.activity
    ON run.activityID = activity.id
  LEFT OUTER JOIN xle.place
    ON event.placeID = place.id
WHERE event.id IN (SELECT
    event.id
  FROM xle.event
    LEFT OUTER JOIN xle.run
      ON event.runID = run.id
    LEFT OUTER JOIN xle.context_run
      ON run.id = context_run.runID
    LEFT OUTER JOIN xle.timeslot
      ON event.timeslotID = timeslot.id
    LEFT OUTER JOIN xle.activity
      ON run.activityID = activity.id
    LEFT OUTER JOIN xle.activity_type
      ON activity.id = activity_type.activityID
    LEFT OUTER JOIN xle.type
      ON activity_type.typeID = type.id
  WHERE context_run.contextID = 30
  AND type.title IN ('Мастер-класс', 'Клуб мышления')
  AND date(timeslot.endDT) = %s
  GROUP BY event.id)
"""

event_department_all = """
SELECT
  event.uuid AS event_uuid,
  type.title AS type_title,
  activity.title AS event_title,
  department.title AS dep_title,
  timeslot.startDT,
  timeslot.endDT
FROM labs.event
  LEFT OUTER JOIN labs.run
    ON event.runID = run.id
  LEFT OUTER JOIN labs.activity
    ON run.activityID = activity.id
  LEFT OUTER JOIN labs.activity_department ad
    ON ad.activityID = activity.id
  LEFT OUTER JOIN labs.context_activity
    ON context_activity.activityID = activity.id
  LEFT OUTER JOIN labs.context
    ON context_activity.contextID = context.id
  LEFT OUTER JOIN labs.activity_type
    ON activity_type.activityID = activity.id
  LEFT OUTER JOIN labs.type
    ON activity_type.typeID = type.id
  LEFT OUTER JOIN labs.department
    ON ad.departmentID = department.id
  LEFT OUTER JOIN labs.timeslot
    ON event.timeslotID = timeslot.id
WHERE context.uuid = '9443f94b-b29f-47b4-bcc8-66a59120f61c'
AND event.isDeleted = 0
AND timeslot.endDT < '2019-07-16'
"""

event_enrolls_all = """
SELECT
  user_info.untiID,
  user_info.leaderID,
  event.uuid AS event_uuid,
  event.title AS event_title,
  timetable.checkin
FROM timetable
  LEFT OUTER JOIN user_info
    ON timetable.userID = user_info.userID
  LEFT OUTER JOIN event
    ON timetable.runID = event.runID
  LEFT OUTER JOIN context_run
    ON timetable.runID = context_run.runID
  LEFT OUTER JOIN context
    ON context_run.contextID = context.id
WHERE context.uuid = '9443f94b-b29f-47b4-bcc8-66a59120f61c'
"""


event_enrolls_all_aggr = """
SELECT
  event.uuid AS event_uuid,
  COUNT(user_info.untiID) AS enrolls_count
FROM xle.timetable
  LEFT OUTER JOIN xle.user_info
    ON timetable.userID = user_info.userID
  LEFT OUTER JOIN xle.event
    ON timetable.runID = event.runID
  LEFT OUTER JOIN xle.context_run
    ON timetable.runID = context_run.runID
  LEFT OUTER JOIN xle.context
    ON context_run.contextID = context.id
WHERE context.uuid = '9443f94b-b29f-47b4-bcc8-66a59120f61c'
GROUP BY event.uuid
"""



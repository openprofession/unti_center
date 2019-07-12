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

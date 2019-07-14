event_material_sum = """
SELECT
  isle_user.leader_id AS leaderID,
  isle_user.unti_id AS untiID,
  isle_event.uid AS event_uuid,
  SUM(isle_eventmaterial.file_size) AS files_sizes,
  COUNT(isle_eventmaterial.file_type) AS files_count
FROM isle_eventmaterial
  LEFT OUTER JOIN isle_user
    ON isle_eventmaterial.user_id = isle_user.id
  LEFT OUTER JOIN isle_event
    ON isle_eventmaterial.event_id = isle_event.id
WHERE isle_eventmaterial.created_at > '2019-07-10'
GROUP BY isle_user.leader_id,
         isle_event.uid
"""

event_material_aggr = """
SELECT
  isle_event.uid AS event_uuid,
  COUNT(DISTINCT(isle_user.leader_id)) AS dtrace_user_count,
  SUM(isle_eventmaterial.file_size) AS files_sizes,
  COUNT(isle_eventmaterial.file_type) AS files_count
FROM isle.isle_eventmaterial
  LEFT OUTER JOIN isle.isle_user
    ON isle_eventmaterial.user_id = isle_user.id
  LEFT OUTER JOIN isle.isle_event
    ON isle_eventmaterial.event_id = isle_event.id
WHERE isle_eventmaterial.created_at > '2019-07-10'
GROUP BY isle_event.uid
"""

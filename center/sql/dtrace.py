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

event_material_aggr_all = """
Select 
  DISTINCT(tt.event_uuid), 
  COUNT(DISTINCT(tt.leader_id)) as dtrace_user_count
FROM
(SELECT
  isle_event.uid AS event_uuid,
  isle_user.leader_id
FROM isle.isle_eventmaterial
  LEFT OUTER JOIN isle.isle_user
    ON isle_eventmaterial.user_id = isle_user.id
  LEFT OUTER JOIN isle.isle_event
    ON isle_eventmaterial.event_id = isle_event.id
WHERE isle_eventmaterial.created_at > '2019-07-10'
UNION 
SELECT
  isle_event.uid,
  isle_user.leader_id
FROM isle.isle_labsuserresult
  LEFT OUTER JOIN isle.isle_labseventresult
    ON isle_labsuserresult.result_id = isle_labseventresult.id
  LEFT OUTER JOIN isle.isle_labseventblock
    ON isle_labseventresult.block_id = isle_labseventblock.id
  LEFT OUTER JOIN isle.isle_event
    ON isle_labseventblock.event_id = isle_event.id
  INNER JOIN isle.isle_user
    ON isle_labsuserresult.user_id = isle_user.id
  INNER JOIN isle.isle_eventtype
    ON isle_event.event_type_id = isle_eventtype.id
) tt
  GROUP BY tt.event_uuid
"""

event_material_all = """
Select 
  CONCAT(tt.leader_id, "_", tt.event_uuid) AS user_event, 
  1 AS dtrace
FROM
(SELECT
  isle_event.uid AS event_uuid,
  isle_user.leader_id
FROM isle.isle_eventmaterial
  LEFT OUTER JOIN isle.isle_user
    ON isle_eventmaterial.user_id = isle_user.id
  LEFT OUTER JOIN isle.isle_event
    ON isle_eventmaterial.event_id = isle_event.id
UNION 
SELECT
  isle_event.uid,
  isle_user.leader_id
FROM isle.isle_labsuserresult
  LEFT OUTER JOIN isle.isle_labseventresult
    ON isle_labsuserresult.result_id = isle_labseventresult.id
  LEFT OUTER JOIN isle.isle_labseventblock
    ON isle_labseventresult.block_id = isle_labseventblock.id
  LEFT OUTER JOIN isle.isle_event
    ON isle_labseventblock.event_id = isle_event.id
  INNER JOIN isle.isle_user
    ON isle_labsuserresult.user_id = isle_user.id
  INNER JOIN isle.isle_eventtype
    ON isle_event.event_type_id = isle_eventtype.id
) tt GROUP BY user_event
  """

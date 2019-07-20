edumap_all = """
SELECT 
  t1.id,
  t1.name,
  SUM(t1.agreements) AS agr_count,
  SUM(t1.projects) AS prj_count,
  SUM(t1.resources) AS res_count
  FROM 
  (SELECT
  map.id,
  map.name,
  COUNT(agreement.name) AS agreements,
  0 AS projects, 
  0 AS resources
FROM map
  LEFT OUTER JOIN agreement_map
    ON agreement_map.map_id = map.id
  LEFT OUTER JOIN agreement
    ON agreement_map.agr_id = agreement.id
GROUP BY map.id
UNION 
SELECT
  map.id,
  map.name,
  0 AS agreements,
  COUNT(project.name) AS projects,
  0 AS resources
FROM map
  LEFT OUTER JOIN project_map
    ON project_map.map_id = map.id
  LEFT OUTER JOIN project
    ON project_map.prj_id = project.id
GROUP BY map.id
UNION 
SELECT
  map.id,
  map.name,
  0 AS agreements,
  0 AS projects, 
  COUNT(resource.name) AS resources
FROM map
  LEFT OUTER JOIN resource_map
    ON resource_map.map_id = map.id
  LEFT OUTER JOIN resource
    ON resource_map.res_id = resource.id
GROUP BY map.id) t1
GROUP BY t1.id
"""

edumap_agr_likes = """
SELECT
  users.leader_id,
  university.name AS u_name,
  agreement.name AS agr_name,
  agreement.subject AS agr_subject,
  agreement.approve_link AS agr_appprove
FROM map_ostrov.agreement_like
  LEFT OUTER JOIN map_ostrov.agreement
    ON agreement_like.agreement_id = agreement.id
  LEFT OUTER JOIN map_ostrov.users
    ON agreement_like.user_id = users.id
  INNER JOIN map_ostrov.university
    ON agreement.u_id = university.id
"""

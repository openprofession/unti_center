all_public_cards = """SELECT
  card.uuid,
  card.reason,
  card.type,
  card.source,
  card.leader_id,
  card.incident_dt,
  st.change_dt,
  st.system,
  st.name AS status,
  st.is_public
FROM redcards.red_cards_status st
  INNER JOIN redcards.red_cards_card card
    ON card.uuid = st.card_id
    AND st.change_dt = (SELECT
        MAX(st2.change_dt) AS expr1
      FROM redcards.red_cards_status st2
      WHERE st2.card_id = st.card_id)
WHERE st.is_public = 1"""

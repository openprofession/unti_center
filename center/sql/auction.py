auction_all = """"""

auction_one_1 = """SELECT
                          auction.uuid AS uuid,
                          auction.title AS title,
                          auction.type AS type,
                          auction.status AS status,
                          auction.startDT AS startDT,
                          auction.endDT AS endDT,
                          CAST(auction.endDT AS date) AS endDate,
                          auction.active AS active,
                          user_auction.bet AS bet,
                          user_auction.priority AS priority,
                          POW(user_auction.priority, (-1) / 3) AS priority_score,
                          user_info.untiID AS untiID,
                          user_info.leaderID AS leaderID,
                          event.uuid AS event_uuid,
                          event.title AS event_title,
                          user_auction.createDT AS bet_dt
                        FROM xle.auction
                          LEFT OUTER JOIN xle.user_auction
                            ON user_auction.auctionID = auction.id
                          LEFT OUTER JOIN xle.user_info
                            ON user_auction.userID = user_info.userID
                          LEFT OUTER JOIN xle.event
                            ON user_auction.eventID = event.id
                        WHERE auction.ID = 1"""

auction_one_2 = """SELECT
                          auction.uuid AS uuid,
                          auction.title AS title,
                          auction.type AS type,
                          auction.status AS status,
                          auction.startDT AS startDT,
                          auction.endDT AS endDT,
                          CAST(auction.endDT AS date) AS endDate,
                          auction.active AS active,
                          user_auction.bet AS bet,
                          user_auction.priority AS priority,
                          POW(user_auction.priority, (-1) / 3) AS priority_score,
                          user_info.untiID AS untiID,
                          user_info.leaderID AS leaderID,
                          event.uuid AS event_uuid,
                          event.title AS event_title,
                          user_auction.createDT AS bet_dt
                        FROM xle.auction
                          LEFT OUTER JOIN xle.user_auction
                            ON user_auction.auctionID = auction.id
                          LEFT OUTER JOIN xle.user_info
                            ON user_auction.userID = user_info.userID
                          LEFT OUTER JOIN xle.event
                            ON user_auction.eventID = event.id
                        WHERE auction.ID = 11"""

auction_one_by_id = """SELECT
                          auction.uuid AS uuid,
                          auction.title AS title,
                          auction.type AS type,
                          auction.status AS status,
                          auction.startDT AS startDT,
                          auction.endDT AS endDT,
                          auction.active AS active,
                          user_auction.bet AS bet,
                          user_auction.priority AS priority,
                          user_info.untiID AS untiID,
                          user_info.leaderID AS leaderID,
                          event.uuid AS event_uuid,
                          event.title AS event_title,
                          user_auction.createDT AS bet_dt
                        FROM xle.auction
                          LEFT OUTER JOIN xle.user_auction
                            ON user_auction.auctionID = auction.id
                          LEFT OUTER JOIN xle.user_info
                            ON user_auction.userID = user_info.userID
                          LEFT OUTER JOIN xle.event
                            ON user_auction.eventID = event.id
                        WHERE auction.ID = %s """

auction_events_1 = """SELECT
                                  timetable.userID,
                                  timetable.type,
                                  event.uuid AS event_uuid,
                                  event.title AS event_title,
                                  activity.sizeMin,
                                  activity.sizeMax
                                FROM xle.auction_timeslot
                                  LEFT OUTER JOIN xle.event
                                    ON auction_timeslot.timeslotID = event.timeslotID
                                  LEFT OUTER JOIN xle.run
                                    ON event.runID = run.id
                                  LEFT OUTER JOIN xle.activity
                                    ON run.activityID = activity.id
                                  LEFT OUTER JOIN xle.timetable
                                    ON run.id = timetable.runID
                                WHERE auction_timeslot.auctionID = 1
                                AND event.uuid <> '8c8beb4b-46cd-4d1f-a51d-ee83213a8198'"""


auction_events_2 = """SELECT
                                  timetable.userID,
                                  timetable.type,
                                  event.uuid AS event_uuid,
                                  event.title AS event_title,
                                  activity.sizeMin,
                                  activity.sizeMax
                                FROM xle.auction_timeslot
                                  LEFT OUTER JOIN xle.event
                                    ON auction_timeslot.timeslotID = event.timeslotID
                                  LEFT OUTER JOIN xle.run
                                    ON event.runID = run.id
                                  LEFT OUTER JOIN xle.activity
                                    ON run.activityID = activity.id
                                  LEFT OUTER JOIN xle.timetable
                                    ON run.id = timetable.runID
                                WHERE auction_timeslot.auctionID = 11"""

auction_events_by_id = """SELECT
                                  timetable.userID,
                                  timetable.type,
                                  event.uuid AS event_uuid,
                                  event.title AS event_title,
                                  activity.sizeMin,
                                  activity.sizeMax
                                FROM xle.auction_timeslot
                                  LEFT OUTER JOIN xle.event
                                    ON auction_timeslot.timeslotID = event.timeslotID
                                  LEFT OUTER JOIN xle.run
                                    ON event.runID = run.id
                                  LEFT OUTER JOIN xle.activity
                                    ON run.activityID = activity.id
                                  LEFT OUTER JOIN xle.timetable
                                    ON run.id = timetable.runID
                                WHERE auction_timeslot.auctionID = %s """

auction_bets_1 = """SELECT
                          auction.uuid AS uuid,
                          auction.title AS title,
                          auction.type AS type,
                          auction.status AS status,
                          auction.startDT AS startDT,
                          auction.endDT AS endDT,
                          auction.active AS active,
                          user_auction.bet AS bet,
                          user_auction.priority AS priority,
                          POW(user_auction.priority, (-1) / 3) AS priority_score,
                          user_info.untiID AS untiID,
                          user_info.leaderID AS leaderID,
                          event.uuid AS event_uuid,
                          event.title AS event_title,
                          user_auction.createDT AS bet_dt
                        FROM xle.auction
                          LEFT OUTER JOIN xle.user_auction
                            ON user_auction.auctionID = auction.id
                          LEFT OUTER JOIN xle.user_info
                            ON user_auction.userID = user_info.userID
                          LEFT OUTER JOIN xle.event
                            ON user_auction.eventID = event.id
                        WHERE auction.ID = 1"""

auction_bets_2 = """SELECT
                          auction.uuid AS uuid,
                          auction.title AS title,
                          auction.type AS type,
                          auction.status AS status,
                          auction.startDT AS startDT,
                          auction.endDT AS endDT,
                          auction.active AS active,
                          user_auction.bet AS bet,
                          user_auction.priority AS priority,
                          POW(user_auction.priority, (-1) / 3) AS priority_score,
                          user_info.untiID AS untiID,
                          user_info.leaderID AS leaderID,
                          event.uuid AS event_uuid,
                          event.title AS event_title,
                          user_auction.createDT AS bet_dt
                        FROM xle.auction
                          LEFT OUTER JOIN xle.user_auction
                            ON user_auction.auctionID = auction.id
                          LEFT OUTER JOIN xle.user_info
                            ON user_auction.userID = user_info.userID
                          LEFT OUTER JOIN xle.event
                            ON user_auction.eventID = event.id
                        WHERE auction.ID = 11"""


auction_bets_by_id = """SELECT
                          auction.uuid AS uuid,
                          auction.title AS title,
                          auction.type AS type,
                          auction.status AS status,
                          auction.startDT AS startDT,
                          auction.endDT AS endDT,
                          auction.active AS active,
                          user_auction.bet AS bet,
                          user_auction.priority AS priority,
                          POW(user_auction.priority, (-1) / 3) AS priority_score,
                          user_info.untiID AS untiID,
                          user_info.leaderID AS leaderID,
                          event.uuid AS event_uuid,
                          event.title AS event_title,
                          user_auction.createDT AS bet_dt
                        FROM xle.auction
                          LEFT OUTER JOIN xle.user_auction
                            ON user_auction.auctionID = auction.id
                          LEFT OUTER JOIN xle.user_info
                            ON user_auction.userID = user_info.userID
                          LEFT OUTER JOIN xle.event
                            ON user_auction.eventID = event.id
                        WHERE auction.ID = %s """


auction_bets_by_date = """SELECT
                          auction.uuid AS uuid,
                          auction.title AS title,
                          auction.type AS type,
                          auction.status AS status,
                          auction.startDT AS startDT,
                          auction.endDT AS endDT,
                          auction.active AS active,
                          user_auction.bet AS bet,
                          user_auction.priority AS priority,
                          user_info.untiID AS untiID,
                          user_info.leaderID AS leaderID,
                          event.uuid AS event_uuid,
                          event.title AS event_title,
                          user_auction.createDT AS bet_dt
                        FROM xle.auction
                          LEFT OUTER JOIN xle.user_auction
                            ON user_auction.auctionID = auction.id
                          LEFT OUTER JOIN xle.user_info
                            ON user_auction.userID = user_info.userID
                          LEFT OUTER JOIN xle.event
                            ON user_auction.eventID = event.id
                        WHERE date(auction.startDt) = %s"""

auction_bets_by_date = """SELECT
                          auction.uuid AS uuid,
                          auction.title AS title,
                          auction.type AS type,
                          auction.status AS status,
                          auction.startDT AS startDT,
                          auction.endDT AS endDT,
                          auction.active AS active,
                          user_auction.bet AS bet,
                          user_auction.priority AS priority,
                          POW(user_auction.priority, (-1) / 3) AS priority_score,
                          user_info.untiID AS untiID,
                          user_info.leaderID AS leaderID,
                          event.uuid AS event_uuid,
                          event.title AS event_title,
                          user_auction.createDT AS bet_dt
                        FROM xle.auction
                          LEFT OUTER JOIN xle.user_auction
                            ON user_auction.auctionID = auction.id
                          LEFT OUTER JOIN xle.user_info
                            ON user_auction.userID = user_info.userID
                          LEFT OUTER JOIN xle.event
                            ON user_auction.eventID = event.id
                        WHERE date(auction.startDt) = %s"""

auction_latest_id = """
SELECT auction.id
FROM xle.auction
WHERE auction.contextID = 30
ORDER BY auction.endDT DESC
LIMIT 1
"""

